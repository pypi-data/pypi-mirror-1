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


import gst
import gtk
import gtk.glade
import goocanvas
import logging

import paramwin
from pad import Pad

class Element(goocanvas.Group):
    """represents GStreamer element"""

    width = 100
    height = 66
    xPadding = 20
    yPadding = 20
    
    def __init__(self, element):
        goocanvas.Group.__init__(self)

        self.model = element
        self.model.set_data("widget", self)
        self.dragHandler = None

        self.box = goocanvas.Rect(parent = self,
                                  width = self.width,
                                  x = -self.width / 2,
                                  line_width = 3,
                                  stroke_color = "black",
                                  fill_color = "grey",
                                  radius_y = 5,
                                  radius_x = 5)

        if element.get_factory():
            name = element.get_factory().get_longname()
        else:
            name = element.get_name()
        self.logger = logging.getLogger(name)
        self.text = goocanvas.Text(parent = self,
                                   text = name,
                                   width = self.width - 2 * self.xPadding,
                                   anchor = gtk.ANCHOR_NORTH,
                                   font = "Sans 9")

        self.model.connect("pad_added", self.onPadAdded)

        self.buttonPressHandler = self.connect("button_press_event", self.onButtonPress)
        self.buttonReleaseHandler = self.connect("button_release_event", self.onButtonRelease)
        
        self.updateLayout()
    
    def logBounds(self):
        b = self.get_bounds()
        self.logger.debug("bounds before adding to table: (%d,%d)  -  (%d,%d)" % (b.x1, b.y1, b.x2, b.y2))
        
    def onPadAdded(self, model, padModel):
        """ Handler for pad_added signal """
        assert(model == self.model)
        self.logger.debug("pad_added: " + str(padModel) + " to " + str(model))
        pad = Pad(padModel)
        self.add_child(pad)
        #check for delayed "linked" handler
        handler = padModel.get_data("link-handler")
        if handler:
            handler()
        self.updateLayout()
        
    def updateLayout(self):
        srcPads = [pad.get_data("widget") for pad in self.model.src_pads()]
        sinkPads = [pad.get_data("widget") for pad in self.model.sink_pads()]

        #update height of box accordingly to pads count
        self.setSize(width = None, height = max(self.height, self.box.props.height, max(len(srcPads), len(sinkPads)) * Pad.radius * 2))

        #update pads positions
        def updatePadsLayout(pads, x):
            for (i, pad) in enumerate(pads):
                if pad:
                    pad.setPosition(x, self.box.props.height / (len(pads) + 1) * (i + 1) - self.box.props.height / 2)

        #update pads y position
        updatePadsLayout(srcPads, self.box.props.width / 2 - self.xPadding / 2)
        updatePadsLayout(sinkPads, -self.box.props.width / 2 + self.xPadding / 2)

    def setPlaying(self):
        "sets the element to playing"
        self.model.set_state(gst.STATE_PLAYING)

    def setPaused(self):
        "sets the element to paused"
        self.model.set_state(gst.STATE_PAUSED)
        
    def setPlayMode(self, state):
        "sets an explicit state for the element"
        self.model.set_state(state)

    def getPlayMode(self):
        "returns the current state of the element"
        (rtrn, current, pending) = self.model.get_state(gst.CLOCK_TIME_NONE)
        return current

    def onButtonPress(self, item, target, event):
        "handle button clicks"
        if event.type == gtk.gdk.BUTTON_PRESS:
            # make this element pop to top
            self.raise_(None)
            if event.button == 1:
                logging.debug("start moving element")
                handler = item.connect("motion_notify_event", self.onMotion, event.x, event.y)
                self.dragHandler = (item, handler)
                return True

            elif event.button == 3:
                popup = gtk.Menu()

                configItem = gtk.ImageMenuItem("Configure Element")
                configImg = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
                configItem.set_image(configImg)
                configItem.connect("activate", self._configure)
                configItem.show()
                popup.attach(configItem, 0, 1, 0, 1)

                deleteItem = gtk.ImageMenuItem("Delete Element")
                deleteImg = gtk.image_new_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_MENU)
                deleteItem.set_image(deleteImg)
                deleteItem.connect("activate", self._delete)
                deleteItem.show()
                popup.attach(deleteItem, 0, 1, 1, 2)
                
                popup.popup(None, None, None, event.button, event.time)
                return True

        #double clicks open the parameter editor window
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self._configure()
            return True
        
    def onMotion(self, item, target, event, startX, startY):
        #drag move
        if event.state & gtk.gdk.BUTTON1_MASK:
            # Get the new position and move by the difference
            (x, y, scale, rotate) = self.get_simple_transform()
            self.setPosition(x + int(event.x - startX), y + int(event.y - startY))

        return True
    
    def onButtonRelease(self, view, target, event):
        "finish dragging"
    
        if self.dragHandler:
            logging.debug("end moving element")
            (item, handler) = self.dragHandler
            item.disconnect(handler)
            self.dragHandler = None

        return True
    
    def _delete(self, event):
        "un-draws the element and cleans up for deletion"
        dialog = gtk.Dialog('Delete Element',
                     self.get_canvas().get_toplevel(),  # the window that spawned this dialog
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,                       
                     (gtk.STOCK_DELETE, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
        dialog.vbox.pack_start(gtk.Label('Are you sure?'))
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.show_all()
        
        rtn = dialog.run()
        if (rtn != gtk.RESPONSE_OK):
            #print "canceled delete"
            pass
        else:
            #delete the ItemView signals for the element and pad views
            #for (item, signal) in self.signals:
            #    item.disconnect(signal)

            #TODO: check this to see if this leaks
            if hasattr(self, "paramWin"):
                del(self.paramWin)
            
            #tell the parent canvas to un-draw and clean up
            self.get_parent().model.remove(self.model)
            
        dialog.destroy()

    def _configure(self, event=None):
        "opens up the config dialog to set element parameters"
        if not(hasattr(self,"paramWin")):
            self.paramWin = paramwin.ParamWin(self.model)
        self.paramWin.show_all()
    
        return True
    
    def remove(self):
        self.model.get_parent().remove(self.model)
        
    def pads(self):
        for pad in self.model.pads():
            widget = pad.get_data("widget")
            yield widget
            if widget.get_child(1):
                yield widget.get_child(1)
            
    def updateLinks(self):
        for pad in self.pads():
            pad.updateLink()
            
    def setPosition(self, x, y):
        self.set_simple_transform(x, y, 1, 0)
                    
        #update the links
        for pad in self.pads():
            if not pad.link:
                continue

            (pad1, pad2) = pad.link.get_data("pads")
            if pad1 == pad:
                point = 0
            elif pad2 == pad:
                point = 1
            else:
                assert(not "link has invalid pads data")

            coords = pad.link.props.points.coords
            coords[point] = pad.link.get_parent().coordsFromChild(pad)
            self.logger.debug("moving link point from " + str(pad.link.props.points.coords[point]) + " to " + str(coords[point]))
            pad.link.props.points = goocanvas.Points(coords)
            
    def setSize(self, width, height):
        if width:
            self.box.props.width = width
            self.box.props.x = -width / 2
            self.text.props.width = width - self.xPadding * 2
        if height:
            self.box.props.height = height
            self.box.props.y = -height / 2
            #self.text.props.height = height - 10
            self.text.props.y = -height / 2 + 5

    def coordsFromChild(self, child):
        x = 0
        y = 0
        while child != self:
            (childX, childY, scale, rotate) = child.get_simple_transform()
            x += childX
            y += childY
            child = child.get_parent()
        
        return (x, y)
    
    def getDownstream(self):
        for pad in self.model.src_pads():
            if pad.get_peer():
                widget = pad.get_peer().get_data("widget")
                if widget and widget.get_parent() and widget.get_parent().__class__ != Pad:
                    yield widget.get_parent()
