#! /usr/bin/env python

##    GstEditor - Gstreamer graphical pipeline editor
##    Copyright (C) 2009 Nickolay Bryskin
##
##    This file is part of GstEditor.
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require("2.0")
import gnome.ui
import gtk
import gtk.glade

import pygst
pygst.require("0.10")
import gst

import sys
from optparse import OptionParser

import logging
import bin
import pad
import goocanvas
import threading

import pkg_resources

import version

class Editor(object):
    "GStreamer Graphical Pipeline Editor class"  
    def __init__(self, name=None):
        "Initialize a new GstEditor"
        
        gnome.init(version.APPNAME, version.APPVERSION)
        self.name = name
        self.pipeline = None
        self.gladefile = pkg_resources.resource_filename(__name__, "gsteditor.glade")
        self.widgets = gtk.glade.XML(self.gladefile, "gstEditorMainWin")
        self.mainwin = self.widgets.get_widget("gstEditorMainWin")
    
        #grab the status bar
        self.statusbar = self.widgets.get_widget("statusbar")
    
        #grab the play button
        self.playButton = self.widgets.get_widget("playButton")
        self.stateCombo = self.widgets.get_widget("stateCombo")
        
        #connect buttons
        signals = {#"destroyWindow": lambda _: gtk.main_quit(),
                   "addElement": self._addElement,
                   "onElementClicked": self._elementClicked,
                   "loadFromFile": self._loadFromFile,
                   "saveToFile": self._saveToFile,
                   "Quit": lambda _: gtk.main_quit(),
                   "About" : self._aboutWindow,
                   "changeState": self._changeState,
                   "setPlayMode": self._setPlayMode,
                   "updateLinks": lambda _: self.pipeline.updateLinks(),
                   "makeNewPipeline": self._makeNewPipeline}
        self.widgets.signal_autoconnect(signals)
        
        #create elements tree
        elementsStore = gtk.TreeStore(object, str)
        
        #build a list of all usable gst elements
        registry = gst.registry_get_default()
        plugins = registry.get_plugin_list()
        plugins.sort(lambda x, y: cmp(x.get_name(), y.get_name()))
        for plugin in plugins:
            parent = elementsStore.append(None, (None, plugin.get_name()))
            features = registry.get_feature_list_by_plugin(plugin.get_name())
            features.sort(lambda x, y: cmp(x.get_name(), y.get_name()))
            for feature in features:
                elementsStore.append(parent, (feature, feature.get_name()))

        #display view
        self.elementsTree = self.widgets.get_widget("elements")
        self.elementsTree.set_model(elementsStore)
        self.elementsTree.append_column(gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=1))
        self.elementsTree.expand_all()

        #create main canvas
        self.canvas = goocanvas.Canvas()
        self.canvas.set_bounds(-100, -100, 100, 100)
        self.canvas.show()
        self.canvas.props.has_tooltip = True
        self.canvas.set_data("widget", self)
        self.widgets.get_widget("canvasSW").add(self.canvas)
        
        #set up drag-n-drop
        self.elementsTree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("text/factory-name", gtk.TARGET_SAME_APP, 0)], gtk.gdk.ACTION_LINK)
#        self.elementsTree.connect("drag_data_get", self._onDragDataGet)
        self.canvas.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("text/factory-name", gtk.TARGET_SAME_APP, 0), ("text/uri-list", 0, 0)], gtk.gdk.ACTION_LINK)
        self.canvas.connect("drag_drop", self._onDragDrop)
        self.canvas.connect("drag_data_received", self._onDragDataReceived)

        #make initial pipeline
        self._makeNewPipeline(None)
        
        #initialize status bar
        self._updatePlayModeDisplay(self.pipeline.getPlayMode())

    def _loadFromFile(self, _widget, _event):
        "Load GST Editor pipeline setup from a file and initialize"
        dialog = gtk.FileChooserDialog("Choose gst file...", self.mainwin, gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        if dialog.run() == gtk.RESPONSE_ACCEPT:
            xml = gst.XML()
            xml.connect("object_loaded", self._onObjectLoaded)
            xml.parse_file(dialog.get_filename(), "pipeline0")
            logging.debug("file loaded")

        dialog.destroy()
        
    def _onObjectLoaded(self, _xml, obj, _node):
        logging.debug("object_loaded: " + str(obj))
        if obj.__class__ == gst.Pipeline:
            bus = obj.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._busMessage)
            logging.debug("pipeline loaded. bus connected")
            self.pipeline = bin.Pipeline(obj)
            self.canvas.set_root_item(self.pipeline)
            self.pipeline.load()
#        else:
#            parent = obj.get_parent()
#            if obj.__class__ == gst.Pad:
#                parent.get_data("widget").onPadAdded(parent, pad)
#            else:
#                parent.get_data("widget").onElementAdded(parent, obj)

    def _saveToFile(self, _widget):
        "Save GST Editor pipeline setup to file"
        dialog = gtk.FileChooserDialog("Choose gst file...", self.mainwin, gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        if dialog.run() == gtk.RESPONSE_ACCEPT:
            gst.xml_write_file(self.pipeline.model, open(dialog.get_filename(), "w"))
            logging.debug("pipeline saved")

        dialog.destroy()
    
    def _aboutWindow(self, _event):
        """ Show the About dialogbox """
        about = gtk.AboutDialog()
        about.set_name(version.APPNAME)
        about.set_version(version.APPVERSION)
        about.set_website("https://launchpad.net/gst-editor")
        about.set_authors(["Brendan Howell <brendan.howell@gmail.com>", "Nickolay Bryskin"])
        about.set_license("GNU General Public License\nSee http://www.gnu.org/licenses/gpl.html for more details")
        about.set_icon_name(self.mainwin.get_icon_name())
    
        about.connect("response", lambda dialog, _: dialog.destroy())
        
        about.show()
        
    def _elementClicked(self, _widget, event):
        """ Add new element if item in the tree double-clicked """
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self._addElement()

    def _onDragDrop(self, _widget, context, _x, _y, time):
        "add new element if item in the tree drag-n-dropped"
        logging.debug("drag-drop")
        
        if "text/factory-name" in context.targets:
            self._addElement()
            context.finish(True, False, time)
            return True
        else:
            return False

    def _onDragDataReceived(self, widget, _context, _x, _y, selection, _info, _time):
        logging.debug("drag-data-received: " + str(selection.get_uris()))
        assert(widget == self.canvas)
        playbin = gst.element_factory_make("playbin", "playbin")
        playbin.props.uri = selection.get_uris()[0]
        self.pipeline.model.add(playbin)

    def _addElement(self, _widget=None, _event=None):
        "adds new element to pipeline"

        #find out which element was selected
        store, select = self.elementsTree.get_selection().get_selected()
        if select and not store.iter_has_child(select):
            #give it to the canvas to instantiate and draw
            self.pipeline.model.add(store.get_value(select, 0).create(None))

        def logItemInfo(item, prefix = " "):
            b = item.get_bounds()
            logging.debug(prefix + str(item) + "\nbounds: (%d,%d)  -  (%d,%d)" % (b.x1, b.y1, b.x2, b.y2))
            for i in range(0, item.get_n_children()):
                logItemInfo(item.get_child(i), prefix + " ")
        
#        logging.debug("items:")
#        logItemInfo(self.canvas.get_root_item())
  
    def _busMessage(self, _bus, message):
        "handles special case where pipeline changes state without a button press"
        logger = logging.getLogger("bus")
        #logger.debug(message)
        if message.type == gst.MESSAGE_STATE_CHANGED:
            (old, new, pending) = message.parse_state_changed()
            logging.debug("status changed: " + str(old) + " -> " + str(new) + " (pending: " + str(pending) + ")")
            self._updatePlayModeDisplay(new)
        elif message.type == gst.MESSAGE_ERROR:
            (_, debug) = message.parse_error()
            logger.error(debug)
        return True
    
    def _updatePlayModeDisplay(self, mode):
        "updates the status bar with current pipeline state"
        cid = self.statusbar.get_context_id("current")
    
        self.statusbar.pop(cid)

        #mode = self.canvas.getPlayMode()
        if mode == gst.STATE_NULL:
            self.statusbar.push(cid, "Pipeline Initialized")
        elif mode == gst.STATE_PAUSED:
            self.statusbar.push(cid, "Pipeline Paused")
        elif mode == gst.STATE_PLAYING:
            self.statusbar.push(cid, "Pipeline Playing")
        elif mode == gst.STATE_READY:
            self.statusbar.push(cid, "Pipeline Ready")
        elif mode == gst.STATE_VOID_PENDING:
            self.statusbar.push(cid, "Pipeline Void Pending")
        else:
            self.statusbar.push(cid, "Pipeline Not Initialized")
            
        #block emission of signal before updating the button
        self.stateCombo.handler_block_by_func(self._changeState)
        self.stateCombo.props.active = mode
        self.stateCombo.handler_unblock_by_func(self._changeState)

        #TODO: sort out wierdness and delays that causes this to be triggered
        # while state is propagating through the pipeline
        # maybe there is a way to filter messages
        
        #block emission of signal before updating the button
        self.playButton.handler_block_by_func(self._setPlayMode)
        self.playButton.set_active(mode == gst.STATE_PLAYING)
        self.playButton.handler_unblock_by_func(self._setPlayMode)

    def _setPlayMode(self, widget):
        "Toggles the Play/Pause button."
        #self.updating = True
        #print "started setting play mode"
        if widget.get_active():
            playmode = gst.STATE_PLAYING
        else:
            playmode = gst.STATE_PAUSED
        self.pipeline.setPlayMode(playmode)
        #TODO: change the widget to make the play mode more visually obvious
        #TODO: attach a signal to update the widget when the element changes state
        #      without a user clicking the button

    def _changeState(self, widget):
        self.pipeline.setPlayMode(widget.props.active)
        
    def _makeNewPipeline(self, _widget):
        self._onObjectLoaded(None, gst.Pipeline(), None)


def main():
    gtk.gdk.threads_init()
    app = Editor("GStreamer pipeline editor")
    return gtk.main()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", type = "int")
    (options, args) = parser.parse_args()
    logging.basicConfig(level = options.debug)
    sys.exit(main())
