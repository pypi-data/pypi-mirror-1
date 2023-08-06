#!/usr/bin/env python

import sys
import gtk
from zope import interface
from gaphor.application import Application
from gaphor.interfaces import IActionProvider
from gaphor.ui.interfaces import IUIComponent
from gaphor.action import action, build_action_group
from gaphor.misc.console import GTKInterpreterConsole
from toplevelwindow import UtilityWindow


class ConsoleWindow(UtilityWindow):
    
    interface.implements(IActionProvider)

    menu_xml = """
        <ui>
          <menubar name="mainwindow">
            <menu action="tools">
              <menuitem action="ConsoleWindow:open" />
            </menu>
          </menubar>
        </ui>
        """

    title = 'Gaphor Console'
    size = (400, 400)
    menubar_path = ''
    toolbar_path = ''

    def __init__(self):
        self.action_group = build_action_group(self)
        self.window = None
        self.ui_manager = None # injected

    def ui_component(self):
        console = GTKInterpreterConsole(locals={
                'service': Application.get_service
                })
        console.show()
        return console

    @action(name='ConsoleWindow:open', label='_Console')
    def open(self):
        if not self.window:
            self.construct()
            self.window.connect('destroy', self.close)
        else:
            self.window.show_all()

    @action(name='ConsoleWindow:close', stock_id='gtk-close', accel='<Control><Shift>w')
    def close(self, window=None):
        self.window.destroy()
        self.window = None

# vim:sw=4:et:ai
