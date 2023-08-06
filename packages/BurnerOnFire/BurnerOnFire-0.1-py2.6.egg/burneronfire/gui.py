#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import threading
import operator

import pygtk
import gtk

from minihallib.HALManager import HALManager
from minihallib.HALDevice import HALDevice
from minihallib.HALPlugin import make_hal_device

from burneronfire.utils import *

pygtk.require('2.0')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
DATA_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(DATA_DIR, 'icons')


class BurnerOnFireGTK(object):
    """Base class for GTK interface"""

    IS_STARTED = False
    MAP_MEDIA_TO_QUANTIFIER = {
        'cd': 172,
        'dvd': 1351.7
    }

    def __init__(self, args):
        from burneronfire import __version__

        self.args = args
        self.filename = None
        self.wrapper = None
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(u'BurnerOnFire v%s' % __version__)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.set_icon_from_file(os.path.join(ICONS_DIR, 'favicon.png'))
        self.statusw = StatusWindow()
        self.statusw.set_transient_for(self.window)

        self.main_vbox = gtk.VBox()

        # signals
        self.window.connect("destroy", self.quit)
        self.statusw.connect("delete_event", self.quit_statusw)

        # ISO FILE
        browse_label = gtk.Label("Choose .ISO file to burn")
        browse_button = gtk.Button(stock=gtk.STOCK_OPEN)
        browse_button.set_size_request(160, 35)
        browse_button.connect("clicked", self.signal_choose_isoimg)

        browse_box = gtk.HBox()
        browse_box.pack_start(browse_label, False)
        browse_box.pack_end(browse_button, False)
        browse_box.set_border_width(5)

        # SPEED
        browse_label = gtk.Label("Specify burning speed")
        self.speed_entry = gtk.combo_box_entry_new_text()
        self.speed_entry.set_size_request(160, 30)
        self.set_write_speeds_from_burners()

        # tooltip for speeds
        info_image = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        info_button = gtk.Button()
        info_button.add(info_image)
        info_button.set_relief(gtk.RELIEF_NONE)
        info_button.set_focus_on_click(False)
        info_button.set_property('has-tooltip', True)
        info_button.connect_object('clicked', BurnerOnFireGTK.set_write_speeds_from_burners, self)
        info_button.connect('query-tooltip', self.on_speeds_tooltip)

        speed_box = gtk.HBox()
        speed_box.pack_start(browse_label, False)
        speed_box.pack_start(info_button, False, padding=3)
        speed_box.pack_end(self.speed_entry, False)

        # MODE
        mode_label = gtk.Label("Specify write mode")
        self.mode_entry = gtk.combo_box_entry_new_text()
        self.mode_entry.child.set_text('dao')
        self.mode_entry.set_size_request(160, 30)
        for option in ['dao', 'sao', 'tao', 'raw', 'raw96r',
            'raw96p', 'raw16', 'clone']:
            self.mode_entry.append_text(option)

        mode_box = gtk.HBox()
        mode_box.pack_start(mode_label, False)
        mode_box.pack_end(self.mode_entry, False)

        # LIMIT
        limit_label = gtk.Label("Number of discs to burn (0=unlimited)")
        self.limit_entry = gtk.Entry()
        self.limit_entry.set_size_request(160, 30)
        self.limit_entry.set_text("0")

        limit_box = gtk.HBox()
        limit_box.pack_start(limit_label, False)
        limit_box.pack_end(self.limit_entry, False)

        # BURN & ABOUT
        about_button = gtk.Button("About", stock=gtk.STOCK_ABOUT)
        about_button.connect("clicked", self.open_about_dialog)
        about_button.set_size_request(130, 45)
        burn_button = gtk.Button()
        burn_label = gtk.Label("_Burn them")
        burn_label.set_property("use-underline", True)
        b_box = gtk.HBox()
        b_box.pack_start(gtk.image_new_from_file(os.path.join(ICONS_DIR, 'burnthem.png')))
        b_box.pack_start(burn_label)
        burn_button.add(b_box)
        burn_button.connect("clicked", self.start_burning)
        burn_button.set_size_request(130, 45)
        submit_box = gtk.HBox()
        submit_box.pack_end(burn_button, False)
        submit_box.pack_start(about_button, False)
        submit_box.set_border_width(1)

        # manage frames
        file_frame = gtk.Frame('File')
        file_frame.add(browse_box)

        options_vbox = gtk.VBox(False, 1)
        options_vbox.set_border_width(5)
        options_vbox.pack_start(speed_box)
        options_vbox.pack_start(mode_box)
        options_vbox.pack_start(limit_box)
        options_frame = gtk.Frame('Options')
        options_frame.add(options_vbox)

        # populate main window
        self.window.add(self.main_vbox)
        self.main_vbox.add(file_frame)
        self.main_vbox.add(options_frame)
        self.main_vbox.add(submit_box)
        self.window.show_all()

    def quit(self, widget):
        if self.wrapper is not None and self.IS_STARTED:
            self.stop_wrapper()
        gtk.main_quit()

    def quit_statusw(self, widget, data=None):
        """Method run when StatusWindow is closed"""
        if self.IS_STARTED:
            self.stop_wrapper()
        widget.hide_all()
        return True

    def stop_wrapper(self):
        from burneronfire import Worker
        if filter(lambda t: isinstance(t, Worker), threading.enumerate()):
            mdialog = gtk.MessageDialog(self.window,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_CLOSE,
                "Some burners are still active.\nWindow will close, " + \
                    "but burners will continue to process.")
            mdialog.run()
            mdialog.destroy()

        self.wrapper.stop()
        self.IS_STARTED = False

    def signal_choose_isoimg(self, widget):
        """Runs dialog to choose ISO image"""
        dialog = gtk.FileChooserDialog("Choose ISO image to burn",
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        # filters
        iso_filter = gtk.FileFilter()
        iso_filter.set_name("ISO image")
        iso_filter.add_pattern("*.iso")
        iso_filter.add_pattern("*.ISO")
        dialog.add_filter(iso_filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.filename = dialog.get_filename()
        dialog.destroy()

    def start_burning(self, widget):
        """Method that starts StatusWindow and burning backend."""
        if self.filename is None:
            mdialog = gtk.MessageDialog(self.window,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_CLOSE,
                "You must first choose .ISO file to burn!")
            mdialog.run()
            mdialog.destroy()
            return

        # start burning...
        self.IS_STARTED = True
        from burneronfire import BurnerOnFire
        bof = BurnerOnFire(self.args + [
                '-%s' % self.mode_entry.child.get_text(),
                'speed=%s' % self.speed_entry.child.get_text()\
                    .strip().split('x', 1)[0],
                self.filename,
            ],
            gui_app=self,
            limit=int(self.limit_entry.get_text().strip())
        )
        self.wrapper = bof.start()
        self.statusw.show_all()
        self.statusw.row_selected(self.statusw.tree_view)

    def open_about_dialog(self, widget):
        from burneronfire import __version__
        ad = gtk.AboutDialog()
        ad.set_name('')
        ad.set_version(str(__version__))
        ad.set_website("http://www.kiberpipa.org/burneronfire")
        ad.set_copyright(u"Domen Kožar")
        ad.set_license(open(os.path.join(DATA_DIR, 'LICENSE.txt')).read())
        ad.set_authors([u'Domen Kožar', u'Jožko Škrablin'])
        ad.set_artists([u'Peter Čuhalev'])
        ad.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(ICONS_DIR,
            'burneronfire_logo.png')))

        ad.run()
        ad.destroy()

    def set_write_speeds_from_burners(self):
        """Implementation to collect write speeds from burners"""
        # TODO: only check for write speed if drive is writable
        m = HALManager()
        self.speed_entry.get_model().clear()

        # get all blank discs
        discs = get_hal_devices('volume.disc')
        discs = filter(lambda d: d.get('volume.disc.is_blank'), discs)
        # TODO: use all burners, if media is cdr

        # write statistics
        self.stats = {
            'win_type': 'None',
            'num_burners': len(get_hal_devices()),
            'num_discs': len(discs),
        }

        if not discs:
            self.speed_entry.child.set_text('')
            return

        # collect media types
        media_types = [disc.get('volume.disc.type').split('_', 1)[0] for disc in discs]

        # count media types
        d = {}
        for type_ in set(media_types):
            d[media_types.count(type_)] = type_

        # get that winner type
        maxed_key = max(d.iterkeys())
        maxed_type = d[maxed_key]
        # TODO: if there are two winners, abort

        # update statistics
        self.stats['win_type'] = maxed_type.upper()

        # filter all non-winning burners
        discs = filter(lambda d: maxed_type in d.get('volume.disc.type'), discs)

        # get all burner speeds
        burners = [make_hal_device(m.bus, disc.get('info.parent')) for disc in discs]
        burners_with_speeds = [set(burner.get('storage.cdrom.write_speeds')) for burner in burners]

        # intersect all write speeds
        write_speeds = reduce(operator.and_, burners_with_speeds)

        # convert to human readable format
        quant = self.MAP_MEDIA_TO_QUANTIFIER.get(maxed_type, 172)
        write_speeds = map(lambda i: int(int(i) / quant), write_speeds)
        write_speeds.sort(reverse=True)

        # update GUI
        self.speed_entry.child.set_text('%dx' % max(write_speeds))
        for option in map(lambda i: '%dx' % i, write_speeds):
            self.speed_entry.append_text(option)

    def on_speeds_tooltip(self, widget, x, y, u, tooltip):
        widget.get_settings().set_property('gtk-tooltip-timeout', 0)
        tooltip.set_markup(STATISTICS_TEXT % self.stats)
        return True

    def main(self):
        gtk.main()


class StatusWindow(gtk.Window):
    """Status window displays what burners are currently doing,
    their logs and how many CD/DVDs were burned.
    """

    def __init__(self):
        super(StatusWindow, self).__init__()
        self.set_title(u'Status')
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_default_size(400, 300)
        self.set_modal(True)
        main_box = gtk.VBox()
        self.add(main_box)

        # make window scrollable
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        main_box.pack_start(sw)

        # get burner devices
        devices = get_hal_devices()

        # populate store
        self.store = gtk.ListStore(str, str, str, str, int, str)
        for device in devices:
            self.store.append([device.get('info.product'),
                               "Idle",
                               device.get('block.device'),
                               "#FFF",
                               0,
                               device.get('info.udi')])
        
        # start treeview
        self.tree_view = gtk.TreeView(self.store)
        self.tree_view.connect("cursor-changed", self.row_selected)
        self.tree_view.connect("button-press-event", self.on_button_press_event)
        self.tree_view.set_rules_hint(True)
        sw.add(self.tree_view)

        # renderers
        rendererText = gtk.CellRendererText()
        rendererProgress = gtk.CellRendererProgress()

        # add columns
        column = gtk.TreeViewColumn("Burner", rendererText, text=0, background=3)
        column.set_sort_column_id(0)
        self.tree_view.append_column(column)
        
        column = gtk.TreeViewColumn("Status", rendererProgress, text=1, value=4)
        column.set_sort_column_id(1)
        column.set_min_width(140)
        self.tree_view.append_column(column)

        column = gtk.TreeViewColumn("Location", rendererText, text=2, background=3)
        column.set_sort_column_id(2)
        self.tree_view.append_column(column)

        # customize columns
        for column in self.tree_view.get_columns():
            column.set_resizable(True)
            column.set_reorderable(True)

        # add stats info
        self.stats_box = gtk.HBox()
        self.stats_box.set_size_request(0, 30)
        main_box.pack_start(self.stats_box, False)

        self.cd_info_text_one = "%d disc burned"
        self.cd_info_text = "%d discs burned"
        self.cd_info = gtk.Label(self.cd_info_text % 0)
        self.stats_box.pack_end(self.cd_info, False, padding=10)

        # setup log buttons
        label_log = gtk.Label("Log")
        label_errlog = gtk.Label("Error log")
        image_filename = os.path.join(ICONS_DIR, 'logfile.png')
        image_log = gtk.image_new_from_file(image_filename)
        image_errlog = gtk.image_new_from_file(image_filename)

        hbox_log = gtk.HBox()
        hbox_log.pack_start(image_log)
        hbox_log.pack_start(label_log)
        self.out_button = gtk.Button()
        self.out_button.add(hbox_log)

        hbox_errlog = gtk.HBox()
        hbox_errlog.pack_start(image_errlog)
        hbox_errlog.pack_start(label_errlog)
        self.err_button = gtk.Button()
        self.err_button.add(hbox_errlog)

        self.stats_box.pack_start(self.out_button, False)
        self.stats_box.pack_start(self.err_button, False)

    def on_button_press_event(self, treeview, event):
        """Device menu to issue Eject"""
        if event.button == 3:
            # extract dev_path from clicked row
            paths = treeview.get_path_at_pos(int(event.x), int(event.y))
            if paths == None:
                return
            iter_ = self.store.get_iter(paths[0])

            # glue menu together
            eject_device = gtk.MenuItem("_Eject")
            close_device = gtk.MenuItem("_Close Tray")
            device_menu = gtk.Menu()
            device_menu.add(eject_device)
            device_menu.add(close_device)
            device_menu.show_all()
            device_menu.popup(None, None, None, event.button, event.time)

            # signals
            eject_device.connect("activate", self.eject_device, iter_)
            close_device.connect("activate", self.close_device, iter_)

    def eject_device(self, menu_item, iter_):
        udi = self.store.get_value(iter_, 5)
        status = self.store.get_value(iter_, 1)

        if 'Idle' not in status:
            self.display_error_message("Could not eject: Burner is burning")
            return

        self.handle_dbus_method(udi, "Eject", "Could not eject")

    def close_device(self, menu_item, iter_):
        udi = self.store.get_value(iter_, 5)
        self.handle_dbus_method(udi, "CloseTray", "Could not close tray")

    def handle_dbus_method(self, udi, method, error_message):
        m = HALManager()
        dev_obj = m.get_dev_obj(udi)
        dev_if = m.get_dev_if(dev_obj, 'org.freedesktop.Hal.Device.Storage')
        dev_method = dev_if.get_dbus_method(method)

        try:
            status = dev_method([])
        except Exception, e:
            self.display_error_message(
                "%s:\n %s" % (error_message, e.message))

    def display_error_message(self, message):
        mdialog = gtk.MessageDialog(self,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_ERROR,
            gtk.BUTTONS_OK,
            message)
        mdialog.run()
        mdialog.destroy()

    def row_selected(self, tree_view):
        """When row is selected, displays Log buttons if appropriate."""
        selection = tree_view.get_selection()
        model, treeiter = selection.get_selected()

        # no selection
        if treeiter is None:
            self.out_button.hide()
            self.err_button.hide()
            return

        burner_name = model.get_value(treeiter, 0)
        dev_path = model.get_value(treeiter, 2)

        # get filenames
        stdout_file = get_logfile_from_burner_name(burner_name, dev_path)
        stderr_file = get_logfile_from_burner_name(burner_name, dev_path, err=True)
        self.out_button.connect_object("clicked", open_file_in_native_app, stdout_file)
        self.err_button.connect_object("clicked", open_file_in_native_app, stderr_file)

        if os.path.isfile(stdout_file):
            self.out_button.show()
        else:
            self.out_button.hide()
        if os.path.isfile(stderr_file):
            self.err_button.show()
        else:
            self.err_button.hide()

    def alter_status_column(self, worker, text):
        """Changes text of a cell."""
        for row in self.store:
            if row[2] == str(worker.dev_path):
                row[1] = text

    def alter_burned_discs(self, worker):
        """This method updates number of burned discs"""
        burned_discs = worker.__class__.NUM_BURNED_DISCS
        if burned_discs == 1:
            self.cd_info.set_text(self.cd_info_text_one % burned_discs)
        else:
            self.cd_info.set_text(self.cd_info_text % burned_discs)

        if burned_discs == worker.limit:
            md = gtk.MessageDialog(self,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_INFO,
                gtk.BUTTONS_CLOSE,
                "%d of %d discs burned. You may now quit BurnerOnFire." %
                    (burned_discs, worker.limit)
            )
            md.run()
            md.destroy()

    def update_progressbar(self, worker, percent):
        """Updates percentage of burner"""
        for row in self.store:
            if row[2] == str(worker.dev_path):
                row[4] = percent
                row[1] = "%d%% done" % percent

STATISTICS_TEXT = \
"""Click this button to refresh burning speed options

<b>You need to insert blank discs in burners to detect burning speeds.</b>

<i>Statistics:</i>
  Total number of burners: %(num_burners)s
  Most common media type: %(win_type)s
  Number of burners taken in account for gathering burning speeds: <b>%(num_discs)s</b>
"""
