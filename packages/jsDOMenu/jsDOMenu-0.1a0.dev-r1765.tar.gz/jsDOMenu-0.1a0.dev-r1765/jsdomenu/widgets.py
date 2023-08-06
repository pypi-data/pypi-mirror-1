from threading import Lock
from os.path import basename, join as path_join

import pkg_resources
import turbogears
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory
from turbogears.i18n import get_locale


static_dir = pkg_resources.resource_filename("jsdomenu", "static")
register_static_directory("jsdomenu", static_dir)

js_dir = 'jsdomenu/javascript'
css_dir = 'jsdomenu/css'

cache = dict()
cache_enabled = turbogears.config.get('jsdomenu.cache.on', False)
cache_lock = Lock()

def getkey(*args, **kw):
    for k,v in kw.iteritems():
        if isinstance(v, list):
            kw[k] = tuple(v)
    new_args = []
    for i in args:
    	new_args.append(isinstance(i, list) and tuple(i) or i)
    args = hash(tuple(new_args))
    return kw and (args, hash(tuple(kw.iteritems()))) or args

def with_lock(func):
    def wrapped(*args, **kw):
        try:
            cache_lock.acquire()
            return func(*args, **kw)
        finally:
            cache_lock.release()
    return wrapped

def cacheit(func):
    def wrapped(*args, **kw):
        if not cache_enabled:
            return func(*args, **kw)
        
        key = getkey(func, get_locale(), *args, **kw)
        
        if not cache.has_key(key):
            cache_lock.acquire()
            try:
                # Verify a second time after locking.
                if not cache.has_key(key):
                    cache[key] = func(*args, **kw)
            finally:
                cache_lock.release()
        
        return cache[key]
    
    wrapped.__name__ = func.__name__
    return wrapped

class BaseItem(object):
    def _set_parent(self, parent):
        self.parent = parent
    def __init__(self, parent=None, **kw):
        super(BaseItem, self).__init__(**kw)
        self.parent = parent

class HasIcon(object):
    def __init__(self, icon=None, **kw):
        super(HasIcon, self).__init__(**kw)
        self.icon = None
        if icon:
            self.add_icon(icon)
    
    def add_icon(self, icon):
        if isinstance(icon, str):
            icon = MenuIcon(file=icon)
        self.icon = icon
        self.icon._set_parent(self)

class Menu(BaseItem, HasIcon):
    """A menu item that containts other items"""
    def __init__(self, name, items=None, sort=False, **kw):
        super(Menu, self).__init__(**kw)
        self.name = name
        self.items = []
        self.sort = sort
        for item in items or []:
            self.add_item(item)
    
    def add_item(self, item):
        self.items.append(item)
        item._set_parent(self)
    
    def remove_item(self, item):
        self.items.remove(item)
        item.parent = None

class MenuItem(BaseItem, HasIcon):
    """A menu item that points to an url"""
    def __init__(self, name, target, **kw):
        super(MenuItem, self).__init__(**kw)
        self.name = name
        self.target = target

class MenuIcon(BaseItem):
    """An icon to decorate a menu item"""
    path = '/static/images/'
    css_template = """
        .%(name)s {
            background-image: url(%(url)s);
            background-repeat: no-repeat; /* Do not alter this line! */
            height: 16px;
            left: 4px;
            position: absolute; /* Do not alter this line! */
            width: 16px;
        }
    """
    
    def __init__(self, file):
        self.file = file
    
    @property
    def safe_name(self):
        return 'menu_icon_' + safe_name(basename(self.file).split('.')[0])
        
    @property
    def url(self):
        return path_join(self.path, self.file)

class Separator(BaseItem):
    """A menu item that generates a separator between items"""
    pass

def safe_name(name):
    return name.replace(' ', '_').lower()

class jsDOMenu(Widget):
    #javascript = [mochikit]
    params = ['menus', 'width', 'type', 'pos_x', 'pos_y', 'theme',
              'target']
    width = 200
    theme = 'classic' # office_xp blue
    type = 'static' # absolute
    pos_x = 10 # only for absolute
    pos_y = 10 # only for absolute
    target = ''
    
    def __init__(self, *args, **kw):
        super(jsDOMenu, self).__init__(*args, **kw)
        self.javascript.append(JSLink(js_dir, 'jsdomenu.js'))
        css = self.theme + '/' + self.theme + '.css'
        self.css.append(CSSLink(css_dir, css))
    
    def generate_menu_declarations(self, menus, width, iframe=None):
        buffer = u''
        for menu in menus:
            for line in self.menu_declaration(menu=menu, width=width,
                                              iframe=iframe):
                buffer += line + '\n'
        return buffer
        
    def generate_menubar_items(self, items):
        buffer = u''
        for item in items:
            name = safe_name(item.name)
            description = item.name
            buffer += u'addMenuBarItem(new menuBarItem("%s", menu_%s));\n' \
                        % (description, name)
        return buffer
    
    def menu_declaration(self, menu, width, iframe=None):
        sub_menus = []
        icons = []
        menu_name = safe_name(menu.name)
        items = menu.items
        yield u'menu_%s = new jsDOMenu(%s, "absolute");' % (menu_name, width)
        yield u'with (menu_%s) {' % menu_name
        
        if menu.sort:
            separated_items = [[]]
            for item in items:
                if isinstance(item, Separator) or item is Separator:
                    separated_items.append(item)
                    separated_items.append([])
                    continue
                separated_items[-1].append(item)
            
            items = []
            for i in separated_items:
                if isinstance(i, list):
                    i.sort(key=lambda x: x.name)
                    items.extend(i)
                elif isinstance(i, Separator) or i is Separator:
                    items.append(i)
        
        for item in items:
            if isinstance(item, Menu):
                target = ''
                sub_menus.append(item)
            elif isinstance(item, MenuItem):
                target = item.target
            elif isinstance(item, Separator) or item is Separator:
                yield u'addMenuItem(new menuItem("-"));'
                continue
            else:
                raise TypeError('Unexpected menu item type')
            if item.icon:
                icons.append(item.icon)
            item_name = safe_name(item.name)
            id = u'menu_%s_%s' % (menu_name, item_name)
            
            if iframe and target:
                target = 'iframe:%s:%s' % (iframe, target)
            
            yield u'addMenuItem(new menuItem("%s", "%s", "%s"));' \
                    % (item.name, id, target)
        yield u'}'
        yield u''
        
        for sub_menu in sub_menus:
            for line in self.menu_declaration(menu=sub_menu, width=width,
                                              iframe=iframe):
                yield line
            yield u''
        
        for sub_menu in sub_menus:
            sub_menu_name = safe_name(sub_menu.name)
            id = u'menu_%s_%s' % (menu_name, sub_menu_name)
            yield u'menu_%s.items.%s.setSubMenu(menu_%s);' \
                    % (menu_name, id, sub_menu_name)
        
        for icon in icons:
            item_name = safe_name(icon.parent.name)
            id = u'menu_%s_%s' % (menu_name, item_name)
            yield u'menu_%s.items.%s.showIcon("%s", "%s");' % (menu_name, id, 
                                                               icon.safe_name,
                                                               icon.safe_name)
        
        yield u''
    
    def generate_icon_definitions(self, menus):
        icons = []
        for menu in menus:
            icons.extend(self.get_icons(menu))
        
        defined_icons = []
        buffer = u''
        for icon in icons:
            if icon.safe_name in defined_icons:
                continue
            defined_icons.append(icon.safe_name)
            buffer += icon.css_template % dict(name=icon.safe_name,
                                               url=icon.url)
        return buffer
    
    def get_icons(self, menu):
        icons = []
        for item in menu.items:
            if getattr(item, 'icon', None):
                icons.append(item.icon)
            if isinstance(item, Menu):
                icons.extend(self.get_icons(item))
        return icons
    
    def update_params(self, d):
        super(jsDOMenu, self).update_params(d)
        d['generate_menu_declarations'] = cacheit(self.generate_menu_declarations)
        d['generate_menubar_items'] = cacheit(self.generate_menubar_items)
        d['generate_icon_definitions'] = cacheit(self.generate_icon_definitions)
        
class jsDOMenuBar(jsDOMenu):
    template = """
    <div id="jsdomenubar" xmlns:py="http://purl.org/kid/ns#">
        <script type="text/javascript">
            function createjsDOMenu() {
                ${generate_menu_declarations(menus=menus, width=width,
                                             iframe=target)}
                
                absoluteMenuBar = new jsDOMenuBar("${type}", "menubar", true);
                with (absoluteMenuBar) {
                    ${generate_menubar_items(items=menus)}
                    moveTo(${pos_x}, ${pos_y});
                }
            }
            
            if (window.onload) {
                old_on_load = window.onload;
                window.onload = function () {old_on_load(); initjsDOMenu();};
            } else {
                window.onload = function () {initjsDOMenu();};
            }
        </script>
        <style type="text/css">
            ${generate_icon_definitions(menus)}
        </style>
        <div id="menubar" style="zoom: 1;">
        </div>
    </div>
    """
    
    def __init__(self, *args, **kw):
        super(jsDOMenuBar, self).__init__(*args, **kw)
        self.javascript.append(JSLink(js_dir, 'jsdomenubar.js'))


