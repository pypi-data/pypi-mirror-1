"""
Basic stuff for toplevel windows.
"""

import os.path
import pkg_resources

import gtk

from zope import interface
from interfaces import IUIComponent

ICONS = (
    'gaphor-24x24.png',
    'gaphor-48x48.png',
    'gaphor-96x96.png',
    'gaphor-256x256.png',
)

class ToplevelWindow(object):

    interface.implements(IUIComponent)

    menubar_path = ''
    toolbar_path = ''

    def __init__(self):
        self.window = None

    def construct(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(True)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(pkg_resources.resource_filename('gaphor.ui', 'pixmaps'))
        icons = (gtk.gdk.pixbuf_new_from_file(os.path.join(icon_dir, f)) for f in ICONS)
        self.window.set_icon_list(*icons)

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        vbox = gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        #self.ui_manager.insert_action_group(self.action_group, 0)
        #self.ui_manager.add_ui_from_string(self.menu_xml)

        menubar = self.ui_manager.get_widget(self.menubar_path)
        if menubar:
            vbox.pack_start(menubar, expand=False)
            #menubar.show()
        
        if self.toolbar_path:
            toolbar = self.ui_manager.get_widget(self.toolbar_path)
            if toolbar:
                vbox.pack_start(toolbar, expand=False)
                #toolbar.show()

        vbox.pack_end(self.ui_component(), expand=True)
        vbox.show()
        # TODO: add statusbar
        self.window.show()


# vim:sw=4:et:ai
