#!/usr/bin/env python
# Copyright (C) 2006, Red Hat, Inc.
# Copyright (C) 2007, One Laptop Per Child
# Copyright (C) 2007 Jan Alonzo <jmalonzo@unpluggable.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import logging
import time
from gettext import gettext as _
from traceback import print_stack

import gtk
import webkit
from pyjamas.__pyjamas__ import pygwt_processMetas, set_main_frame
from pyjamas import DOM

def module_load(m, load):
    print m
    minst = None
    exec """\
from %(mod)s import %(mod)s
minst = %(mod)s()
if load:
    minst.onModuleLoad()
""" % ({'mod': m})
    return minst

class WebToolbar(gtk.Toolbar):
    def __init__(self, browser):
        gtk.Toolbar.__init__(self)

        self._browser = browser

        # navigational buttons
        self._back = gtk.ToolButton(gtk.STOCK_GO_BACK)
        self._back.set_tooltip(gtk.Tooltips(),_('Back'))
        self._back.props.sensitive = False
        self._back.connect('clicked', self._go_back_cb)
        self.insert(self._back, -1)

        self._forward = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        self._forward.set_tooltip(gtk.Tooltips(),_('Forward'))
        self._forward.props.sensitive = False
        self._forward.connect('clicked', self._go_forward_cb)
        self.insert(self._forward, -1)
        self._forward.show()

        self._stop_and_reload = gtk.ToolButton(gtk.STOCK_REFRESH)
        self._stop_and_reload.set_tooltip(gtk.Tooltips(),_('Stop and reload current page'))
        self._stop_and_reload.connect('clicked', self._stop_and_reload_cb)
        self.insert(self._stop_and_reload, -1)
        self._stop_and_reload.show()
        self._loading = False

        self.insert(gtk.SeparatorToolItem(), -1)

        # zoom buttons
        self._zoom_in = gtk.ToolButton(gtk.STOCK_ZOOM_IN)
        self._zoom_in.set_tooltip(gtk.Tooltips(), _('Zoom in'))
        self._zoom_in.connect('clicked', self._zoom_in_cb)
        self.insert(self._zoom_in, -1)
        self._zoom_in.show()

        self._zoom_out = gtk.ToolButton(gtk.STOCK_ZOOM_OUT)
        self._zoom_out.set_tooltip(gtk.Tooltips(), _('Zoom out'))
        self._zoom_out.connect('clicked', self._zoom_out_cb)
        self.insert(self._zoom_out, -1)
        self._zoom_out.show()

        self._zoom_hundred = gtk.ToolButton(gtk.STOCK_ZOOM_100)
        self._zoom_hundred.set_tooltip(gtk.Tooltips(), _('100% zoom'))
        self._zoom_hundred.connect('clicked', self._zoom_hundred_cb)
        self.insert(self._zoom_hundred, -1)
        self._zoom_hundred.show()

        self.insert(gtk.SeparatorToolItem(), -1)

        # location entry
        self._entry = gtk.Entry()
        self._entry.connect('activate', self._entry_activate_cb)
        self._current_uri = None

        entry_item = gtk.ToolItem()
        entry_item.set_expand(True)
        entry_item.add(self._entry)
        self._entry.show()

        self.insert(entry_item, -1)
        entry_item.show()

        # scale other content besides from text as well
        self._browser.set_full_content_zoom(True)

        self._browser.connect("title-changed", self._title_changed_cb)

    def set_loading(self, loading):
        self._loading = loading

        if self._loading:
            self._show_stop_icon()
            self._stop_and_reload.set_tooltip(gtk.Tooltips(),_('Stop'))
        else:
            self._show_reload_icon()
            self._stop_and_reload.set_tooltip(gtk.Tooltips(),_('Reload'))
        self._update_navigation_buttons()

    def _set_address(self, address):
        self._entry.props.text = address
        self._current_uri = address

    def _update_navigation_buttons(self):
        can_go_back = self._browser.can_go_back()
        self._back.props.sensitive = can_go_back

        can_go_forward = self._browser.can_go_forward()
        self._forward.props.sensitive = can_go_forward

    def _entry_activate_cb(self, entry):
        self._browser.open(entry.props.text)

    def _go_back_cb(self, button):
        self._browser.go_back()

    def _go_forward_cb(self, button):
        self._browser.go_forward()

    def _title_changed_cb(self, widget, frame, title):
        self._set_address(frame.get_uri())

    def _stop_and_reload_cb(self, button):
        if self._loading:
            self._browser.stop_loading()
        else:
            self._browser.reload()

    def _show_stop_icon(self):
        self._stop_and_reload.set_stock_id(gtk.STOCK_CANCEL)

    def _show_reload_icon(self):
        self._stop_and_reload.set_stock_id(gtk.STOCK_REFRESH)

    def _zoom_in_cb (self, widget):
        """Zoom into the page"""
        self._browser.zoom_in()

    def _zoom_out_cb (self, widget):
        """Zoom out of the page"""
        self._browser.zoom_out()

    def _zoom_hundred_cb (self, widget):
        """Zoom 100%"""
        if not (self._browser.get_zoom_level() == 1.0):
            self._browser.set_zoom_level(1.0);

class BrowserPage(webkit.WebView):
    def __init__(self):
        webkit.WebView.__init__(self)

class WebStatusBar(gtk.Statusbar):
    def __init__(self):
        gtk.Statusbar.__init__(self)
        self.iconbox = gtk.EventBox()
        self.iconbox.add(gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON))
        self.pack_start(self.iconbox, False, False, 6)
        self.iconbox.hide_all()

    def display(self, text, context=None):
        cid = self.get_context_id("pywebkitgtk")
        self.push(cid, str(text))

    def show_javascript_info(self):
        self.iconbox.show()

    def hide_javascript_info(self):
        self.iconbox.hide()


class WebBrowser(gtk.Window):
    def __init__(self, application, appdir=None):
        gtk.Window.__init__(self)

        self.already_initialised = False

        logging.debug("initializing web browser window")

        self._loading = False
        self._browser= BrowserPage()
        #self._browser.connect('load-started', self._loading_start_cb)
        #self._browser.connect('load-progress-changed', self._loading_progress_cb)
        self._browser.connect('load-finished', self._loading_stop_cb)
        self._browser.connect("title-changed", self._title_changed_cb)
        self._browser.connect("hovering-over-link", self._hover_link_cb)
        self._browser.connect("status-bar-text-changed", self._statusbar_text_changed_cb)
        self._browser.connect("icon-loaded", self._icon_loaded_cb)
        self._browser.connect("selection-changed", self._selection_changed_cb)
        self._browser.connect("set-scroll-adjustments", self._set_scroll_adjustments_cb)
        self._browser.connect("populate-popup", self._populate_popup)
#        self._browser.connect("navigation-requested", self._navigation_requested_cb)

        self._browser.connect("console-message",
                              self._javascript_console_message_cb)
        self._browser.connect("script-alert",
                              self._javascript_script_alert_cb)
        self._browser.connect("script-confirm",
                              self._javascript_script_confirm_cb)
        self._browser.connect("script-prompt",
                              self._javascript_script_prompt_cb)

        self._scrolled_window = gtk.ScrolledWindow()
        self._scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.add(self._browser)
        self._scrolled_window.show_all()

        self._toolbar = WebToolbar(self._browser)

        self._statusbar = WebStatusBar()

        vbox = gtk.VBox(spacing=4)
        vbox.pack_start(self._toolbar, expand=False, fill=False)
        vbox.pack_start(self._scrolled_window)
        vbox.pack_end(self._statusbar, expand=False, fill=False)

        self.add(vbox)
        self.set_default_size(600, 480)

        self.connect('destroy', gtk.main_quit)

        if os.path.isfile(application):
            
            (pth, app) = os.path.split(application)
            if appdir:
                pth = os.path.abspath(appdir)
            sys.path.append(pth)

            m = None
            # first, pretend it's a module. if success, create fake template
            # otherwise, treat it as a URL
            if application[-3:] == ".py":

                try:
                    m = module_load(app[:-3], False)
                except ImportError, e:
                    print_stack()
                    print e
                    m = None

            if m is None:
                application = os.path.abspath(application)
                print application
                self._browser.open(application)
            else:
                # it's a python app.
                if application[-3:] != ".py":
                    print "Application %s must be a python file (.py)"
                    sys.exit(-1)
                # ok, we create a template with the app name in it:
                # pygwt_processMetas will pick up the app name
                # and do the load, there.  at least this way we
                # have a basic HTML page to start off with,
                # including a possible stylesheet.
                fqp = os.path.abspath(application[:-3])
                template = """
<html>
    <head>
        <meta name="pygwt:module" content="%(app)s" />
        <link rel="stylesheet" href="%(app)s.css" />
        <title>%(app)s</title>
    </head>
    <body bgcolor="white" color="white">
        <iframe id='__pygwt_historyFrame' style='width:0px;height:0px;border:0px;margin:0px;padding:0px;display:none;'></iframe>
    </body>
</html>
""" % {'app': app[:-3]}

                print template
                self._browser.load_string(template, "text/html", "iso-8859-15", fqp)
        else:
            # URL.
            
            sys.path.append(os.path.abspath(os.getcwd()))
            self._browser.open(application)


        self.show_all()

    def init_app(self):
        # TODO: ideally, this should be done by hooking body with an "onLoad".

        main_frame = self._browser.get_main_frame()
        set_main_frame(main_frame)

        gdoc = main_frame.get_gdom_document()

        for m in pygwt_processMetas():
            module_load(m, True)

    def _set_title(self, title):
        self.props.title = title

    def _loading_start_cb(self, view, frame):
        main_frame = self._browser.get_main_frame()
        if frame is main_frame:
            self._set_title(_("Loading %s - %s") % (frame.get_title(),frame.get_uri()))
        self._toolbar.set_loading(True)

    def _loading_stop_cb(self, view, frame):
        # FIXME: another frame may still be loading?
        self._toolbar.set_loading(False)

        if self.already_initialised:
            return
        self.already_initialised = True
        self.init_app()

    def _loading_progress_cb(self, view, progress):
        self._set_progress(_("%s%s loaded") % (progress, '%'))

    def _set_progress(self, progress):
        self._statusbar.display(progress)

    def _title_changed_cb(self, widget, frame, title):
        self._set_title(_("%s") % title)

    def _hover_link_cb(self, view, title, url):
        if view and url:
           self._statusbar.display(url)
        else:
           self._statusbar.display('')

    def _statusbar_text_changed_cb(self, view, text):
        #if text:
        self._statusbar.display(text)

    def _icon_loaded_cb(self):
        print "icon loaded"

    def _selection_changed_cb(self):
        print "selection changed"

    def _set_scroll_adjustments_cb(self, view, hadjustment, vadjustment):
        self._scrolled_window.props.hadjustment = hadjustment
        self._scrolled_window.props.vadjustment = vadjustment

    def _navigation_requested_cb(self, view, frame, networkRequest):
        return 1

    def _javascript_console_message_cb(self, view, message, line, sourceid):
        self._statusbar.show_javascript_info()

    def _javascript_script_alert_cb(self, view, frame, message):

        print "alert", message
        return
        def close(w):
            dialog.destroy()
        #win = GetRootWindow()
        dialog = gtk.Dialog("Alert", None, gtk.DIALOG_DESTROY_WITH_PARENT)
        #dialog.Modal = True;
        label = gtk.Label(message)
        dialog.vbox.add(label)
        label.show()
        button = gtk.Button("OK")
        dialog.action_area.pack_start (button, True, True, 0)
        button.connect("clicked", close)
        button.show()
        #dialog.Response += new ResponseHandler (on_dialog_response)
        print dir(dialog)
        dialog.run ()

    def _javascript_script_confirm_cb(self, view, frame, message, isConfirmed):
        pass

    def _browser_event_cb(self, view, event, message, fromwindow):
        print "event! wha-hey!", event, view, message
        print event.get_event_type()
        #event.stop_propagation()
        return True

    def _javascript_script_prompt_cb(self, view, frame, message, default, text):
        pass

    def _populate_popup(self, view, menu):
        aboutitem = gtk.MenuItem(label="About PyWebKit")
        menu.append(aboutitem)
        aboutitem.connect('activate', self._about_pywebkitgtk_cb)
        menu.show_all()

    def _about_pywebkitgtk_cb(self, widget):
        self._browser.open("http://live.gnome.org/PyWebKitGtk")



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "usage: %s application[.py|.html]" % sys.argv[0]
        sys.exit(-1)
    if len(sys.argv) == 3:
        appdir = sys.argv[2]
    else:
        appdir = None
    webbrowser = WebBrowser(sys.argv[1], appdir)
    gtk.main()

