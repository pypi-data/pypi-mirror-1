# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2008 Brisa Team <brisa-develop@garage.maemo.org>

from brisa.core.reactors import Gtk2Reactor
reactor = Gtk2Reactor()

import dbus
import gtk
import gtk.glade
import subprocess

from os.path import join, dirname

from brisa.utils.looping_call import LoopingCall
from brisa.core import log

cur_dir = dirname(__file__)

MSERVER_IF = 'br.edu.ufcg.embedded.brisa.MediaServer'
MRENDERER_IF = 'br.edu.ufcg.embedded.brisa.MediaRenderer'

MSERVER_OBJ_PATH = '/br/edu/ufcg/embedded/brisa/MediaServer'
MRENDERER_OBJ_PATH = '/br/edu/ufcg/embedded/brisa/MediaRenderer'

bus = dbus.SessionBus()


class ControlGUI(object):

    def __init__(self):
        self.server_proxy = None
        self.renderer_proxy = None
        self.glade = gtk.glade.XML(join(cur_dir, 'control.glade'))
        self.main_window = self.glade.get_widget('control')
        self.renderer_window = self.glade.get_widget('renderer_window')
        self.server_window = self.glade.get_widget('server_window')
        self.main_window.connect('destroy', self.quit)
        self.renderer_window.connect('destroy', self.quit)
        self.server_window.connect('destroy', self.quit)
        self.main_window.set_icon_from_file(join(cur_dir, 'brisa.png'))
        self.renderer_window.set_icon_from_file(join(cur_dir, 'brisa.png'))
        self.server_window.set_icon_from_file(join(cur_dir, 'brisa.png'))

        signals = {'on_server_clicked': self._show_server,
                   'on_renderer_clicked': self._show_renderer,
                   'on_start_clicked': self.toggle_server,
                   'on_start1_clicked': self.toggle_renderer,
                   'on_rescan_clicked': self.server_rescan,
                   'on_reload_clicked': self.server_reload,
                   'on_config_clicked': self.server_config}
        self.glade.signal_autoconnect(signals)
        back = self.glade.get_widget('back')
        back1 = self.glade.get_widget('back1')
        back.connect('clicked', self._show_main, self.server_window)
        back1.connect('clicked', self._show_main, self.renderer_window)
        self.looping_call = LoopingCall(self._refresh)
        self.button_image = self.glade.get_widget('bt_image')
        self.button_label = self.glade.get_widget('bt_label')
        self.button_image1 = self.glade.get_widget('bt_image1')
        self.button_label1 = self.glade.get_widget('bt_label1')

    def run(self):
        self.main_window.show()
        self.looping_call.start(1)
        reactor.main()

    def quit(self, widget=None):
        reactor.main_quit()

    def _refresh(self):
        self._update_server_button()
        self._update_server_label()
        self._update_renderer_button()
        self._update_renderer_label()

    def _show_server(self, widget):
        self.main_window.hide()
        self._update_server_label()
        self.glade.get_widget('server_window').show()

    def _show_renderer(self, widget):
        self.main_window.hide()
        self._update_renderer_label()
        self.glade.get_widget('renderer_window').show()

    def _show_main(self, widget, window):
        window.hide()
        self.main_window.show()

    def toggle_server(self, widget):
        if not self.get_server_status():
            dialog = gtk.MessageDialog(self.main_window,
                                       type=gtk.MESSAGE_QUESTION,
                                       buttons=gtk.BUTTONS_YES_NO,
                                       message_format='It might take a while'\
                                       ' to start the media server. Do you'\
                                       ' want to continue?')
            dialog.set_position(gtk.WIN_POS_CENTER)
            dialog.set_modal(True)
            result = dialog.run()
            if result == gtk.RESPONSE_YES:
                dialog.destroy()
                self.start_server()
            else:
                dialog.destroy()
        else:
            self.stop_server()

    def toggle_renderer(self, widget):
        if not self.get_renderer_status():
            dialog = gtk.MessageDialog(self.main_window,
                                       type=gtk.MESSAGE_QUESTION,
                                       buttons=gtk.BUTTONS_YES_NO,
                                       message_format='It might take a while'\
                                       ' to start the media renderer. Do you'\
                                       ' want to continue?')
            dialog.set_position(gtk.WIN_POS_CENTER)
            dialog.set_modal(True)
            result = dialog.run()
            if result == gtk.RESPONSE_YES:
                dialog.destroy()
                self.start_renderer()
            else:
                dialog.destroy()
        else:
            self.stop_renderer()

    def server_rescan(self, widget):
        proxy = self.get_server_proxy()
        rescan_method = proxy.get_dbus_method('dms_cds_rescan_folders', MSERVER_IF)
        try:
            rescan_method()
        except Exception, e:
            log.debug('Could not rescan folders. Reason %s' % e.message)

    def server_reload(self, widget):
        proxy = self.get_server_proxy()
        reload = proxy.get_dbus_method('dms_reload_config', MSERVER_IF)
        try:
            reload()
        except Exception, e:
            log.debug('Could not reload config. Reason: %s' % e.message)

    def server_config(self, widget):
        subprocess.Popen('brisa-media-server-conf', shell=True)

    def get_server_proxy(self):
        if not self.server_proxy:
            self.server_proxy = bus.get_object(MSERVER_IF, MSERVER_OBJ_PATH)
        if not self.server_proxy:
            raise Exception('Could not retrieve server proxy.')

        return self.server_proxy

    def get_renderer_proxy(self):
        if not self.renderer_proxy:
            self.renderer_proxy = bus.get_object(MRENDERER_IF,
                                                 MRENDERER_OBJ_PATH)
        if not self.renderer_proxy:
            raise Exception('Could not retrieve renderer proxy.')

        return self.renderer_proxy

    def start_renderer(self):
        if not self.get_renderer_status():
            # This already brings up from the .service file
            self.renderer_proxy = None
            self.get_renderer_proxy()

    def start_server(self):
        if not self.get_server_status():
            # This already brings up from the .service file
            self.server_proxy = None
            self.get_server_proxy()

    def stop_server(self):
        proxy = self.get_server_proxy()
        stop_method = proxy.get_dbus_method('dms_halt', MSERVER_IF)
        try:
            stop_method()
        except Exception, e:
            self.server_proxy = None
            log.debug('Could not stop server. Reason: %s' % e.message)

    def stop_renderer(self):
        proxy = self.get_renderer_proxy()
        stop_method = proxy.get_dbus_method('dmr_halt', MRENDERER_IF)
        try:
            stop_method()
        except Exception, e:
            self.renderer_proxy = None
            log.debug('Could not stop renderer. Reason: %s' % e.message)

    def get_server_status(self):
        return bus.name_has_owner(MSERVER_IF)

    def get_server_info(self):
        proxy = self.get_server_proxy()
        info_method = proxy.get_dbus_method('dms_get_server_info', MSERVER_IF)
        try:
            return info_method()
        except Exception, e:
            self.server_proxy = None
            log.debug('Could not retrieve server info. Reason: %s' % e.message)
            return ('', ) * 7

    def get_renderer_status(self):
        return bus.name_has_owner(MRENDERER_IF)

    def get_renderer_info(self):
        proxy = self.get_renderer_proxy()
        info_method = proxy.get_dbus_method('dmr_get_renderer_info', MRENDERER_IF)
        try:
            return info_method()
        except Exception, e:
            self.renderer_proxy = None
            log.debug('Could not retrieve renderer info. Reason: %s' %
                      e.message)
            return ('', ) * 6

    def _update_server_button(self):
        self.button_image.hide()
        self.button_label.hide()
        if self.get_server_status():
            self.button_image.set_from_stock('gtk-stop', gtk.ICON_SIZE_BUTTON)
            self.button_label.set_text('Stop')
        else:
            self.button_image.set_from_stock('gtk-yes', gtk.ICON_SIZE_BUTTON)
            self.button_label.set_text('Start')
        self.button_image.show()
        self.button_label.show()

    def _update_renderer_button(self):
        self.button_image1.hide()
        self.button_label1.hide()
        if self.get_renderer_status():
            self.button_image1.set_from_stock('gtk-stop', gtk.ICON_SIZE_BUTTON)
            self.button_label1.set_text('Stop')
        else:
            self.button_image1.set_from_stock('gtk-yes', gtk.ICON_SIZE_BUTTON)
            self.button_label1.set_text('Start')
        self.button_image1.show()
        self.button_label1.show()

    def _update_server_label(self):
        label = self.glade.get_widget('server_label')
        status = self.get_server_status()

        s = 'Status: %s' % {True: 'running', False: 'stopped'}.\
            get(status)

        if status:
            info = self.get_server_info()
        else:
            info = ('', ) * 7

        s += '\nServer Name: %s' % info[3]
        s += '\nDevice: %s' % info[0]
        s += '\nApp. Version: %s' % info[2]
        s += '\nBRisa Version: %s' % info[1]
        s += '\nXBox Compatible: %s' % info[4]
        s += '\nLogging Level: %s' % info[5]
        s += '\nLogging Output: %s' % info[6]
        label.set_text(s)

    def _update_renderer_label(self):
        label = self.glade.get_widget('renderer_label')
        status = self.get_renderer_status()

        s = 'Status: %s' % {True: 'running', False: 'stopped'}.\
            get(status)

        if status:
            info = self.get_renderer_info()
        else:
            info = ('', ) * 6

        s += '\nRenderer Name: %s' % info[3]
        s += '\nDevice: %s' % info[0]
        s += '\nApp. Version: %s' % info[2]
        s += '\nBRisa Version: %s' % info[1]
        s += '\nLogging Level: %s' % info[4]
        s += '\nLogging Output: %s' % info[5]
        label.set_text(s)


def main():
    g = ControlGUI()
    reactor.add_after_stop_func(g.quit)
    g.run()
