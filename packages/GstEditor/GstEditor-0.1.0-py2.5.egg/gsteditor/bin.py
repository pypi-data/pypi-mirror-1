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
import goocanvas
import logging
import pygraphviz
from element import Element
from pad import Pad

class Bin(Element):
    """GooCanvas widget for GStreamer bin"""
    
    width = Element.width + 2 * Element.xPadding
    height = Element.height + 2 * Element.yPadding

    def __init__(self, bin):
        Element.__init__(self, bin)
        
#        self.elementsCount = 0

        self.box.props.fill_color = "brown"

        self.model.connect("element_added", self.onElementAdded)
        self.model.connect("element_removed", self.onElementRemoved)
            
#        Element.updateLayout(self)

    def onElementAdded(self, bin, element):
        """Called when element added by hands or bins (such as Playbin)"""
        self.logger.debug("element_added: " + str(element))
        assert(self.model == bin)
        widget = self.addElement(element)
        for pad in widget.pads():
            #make handler for connecting pads
            pad.updateLink()
            pad.widget.connect("button_press_event", self._startDrag)

    def addElement(self, element):
        """ Makes job of adding element """
        #create our widget
        if issubclass(element.__class__, gst.Bin):
            widget = Bin(element)
        elif issubclass(element.__class__, gst.Element):
            widget = Element(element)
        self.add_child(widget)
        #create widgets for it's pads 
        for padModel in widget.model.pads():
            self.logger.debug("adding existing pad")
            widget.onPadAdded(widget.model, padModel)
        widget.logBounds()
        self.updateLayout()
        if issubclass(element.__class__, gst.Bin):
            #add each child that already inside the bin
            for child in element.elements():
                self.logger.debug("adding existing child")
                widget.onElementAdded(element, child)
        return widget

    def updateLayout(self):
        """update layout of all child elements"""
        #filter elements without widget
        elements = filter(None, [element.get_data("widget") for element in self.model.sorted()])

        nodes = dict()

        #create our graph for layouting items
        graph = pygraphviz.AGraph(directed = True,
                                  strict = True)

        #add all elements to graph as nodes
        for element in elements:
            graph.add_node(element,
                           fixedsize = "true",
                           height = str(element.box.props.width / 60),
                           width = str(element.box.props.height / 60),
                           shape = "box",
                           fontsize = "1")
            nodes[str(element)] = element
            self.logger.debug("node added: " + str(element))

        #add all links to graph as edges
        for element in reversed(elements):
            for sink in element.getDownstream():
                graph.add_edge(element, sink)
                self.logger.debug("edge added: " + str(element) + " -> " + str(sink))
                nodes[str(sink)] = sink

        #layout elements
        graph.layout(prog="dot")

        #now normalize element coordinates

        class Bounds(object):
            def __init__(self, x1 = 1000000, y1 = 1000000, x2 = -1000000, y2 = -1000000):
                self.x1 = x1
                self.y1 = y1
                self.x2 = x2
                self.y2 = y2
                
            def __str__(self):
                return "Bounds: (%d, %d) - (%d, %d)" % (self.x1, self.y1, self.x2, self.y2) 

            def update(self, x, y, width = 0, height = 0):
                self.x1 = min(self.x1, x - width / 2)
                self.y1 = min(self.y1, y - height / 2)
                self.x2 = max(self.x2, x + width / 2)
                self.y2 = max(self.y2, y + height / 2)

            def getWidth(self):
                return self.x2 - self.x1

            def getHeight(self):
                return self.y2 - self.y1

            def getMiddleX(self):
                return (self.x1 + self.x2) / 2

            def getMiddleY(self):
                return (self.y1 + self.y2) / 2

            width = property(getWidth)
            height = property(getHeight)
            middleX = property(getMiddleX)
            middleY = property(getMiddleY)

        bounds = Bounds()

        for node in graph.nodes():
            (y, x) = eval(node.attr["pos"])
            self.logger.debug("Node %s: %s" % (node, (x, y)))
            bounds.update(x, y, nodes[node].box.props.width, nodes[node].box.props.height)

        self.logger.debug("Middles %f %f" % (bounds.middleX, bounds.middleY))

        for node in graph.nodes():
            (y, x) = eval(node.attr["pos"])
            x -= bounds.middleX
            y -= bounds.middleY
            self.logger.debug("Element %s: %s" % (node, (x, y)))
            nodes[node].setPosition(-x, y)

        self.setSize(width = max(self.width, bounds.width + self.xPadding * 2),
                     height = max(self.height, bounds.height + self.yPadding * 2))

        #update layout of pads
        Element.updateLayout(self)

        #update parent layout (for case of bounds change)
        if self.get_parent():
            self.get_parent().updateLayout()

        #update links points
        for n in range(0, self.get_n_children()):
            child = self.get_child(n)
            if child.__class__ == goocanvas.Polyline:
                coords = child.props.points.coords
                pads = child.get_data("pads")
                coords[0] = self.coordsFromChild(pads[0])
                coords[1] = self.coordsFromChild(pads[1])
                child.props.points = goocanvas.Points(coords)

    def onElementRemoved(self, bin, element):
        "remove widgets for element itself, it's pads and links"
        assert(bin == self.model)
        self.logger.debug("element_removed: " + str(element))
        child = self.find_child(element.get_data("widget"))
        self.remove_child(child)
        self.updateLayout()

    def makeLink(self, pad1, pad2):
        "make link widget or return existed"
        
        link = goocanvas.Polyline()
        link.props.points = goocanvas.Points([self.coordsFromChild(pad1), self.coordsFromChild(pad2)])
        self.logger.debug("makeLink: " + str(link.props.points.coords))
        link.set_data("pads", (pad1, pad2))
        self.add_child(link)
        
        #this code raises assertion in goocanvas
        link.lower(pad1.get_parent())
        link.lower(pad2.get_parent())

        return link

    def destroyLink(self, link):
        "removes a link from the canvas and cleans up"
        self.remove_child(self.find_child(link))

    def _onLinkClick(self, view, target, event):
        "handler for link clicks"
        self.pointer_ungrab(view, 0)
        
        logging.debug("clicked on a link")

    def _startDrag(self, view, pad, event):
        "start a new link drag"
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            logging.debug("starting drag. event: %d %d" % (event.x, event.y))
            assert(pad == view)

            #convert coordinates from pad space to our (bin) space
            #TODO: make it without canvas
            coords2 = self.get_canvas().convert_to_item_space(self, event.x_root, event.y_root)

            #make the new link
            points = goocanvas.Points([self.coordsFromChild(pad), coords2])
            link = goocanvas.Polyline()
            link.props.points = points

            #save reference to source pad instead of calculating it from source coords each time
            link.set_data("pad", pad)

            self.add_child(link)

            link.lower(pad)

            #now watch for these events so we can catch 
            handler1 = pad.connect("motion_notify_event", self._doDrag, link)
            handler2 = pad.connect("button_release_event", self._stopDrag, link)
            link.set_data("handlers", [handler1, handler2])

        return True

    def _doDrag(self, view, pad, event, link):
        "update link end point"
        assert(pad == view)
        
        self.logger.debug("doDrag. event: %d %d" % (event.x, event.y))

        coords2 = self.get_canvas().convert_to_item_space(self, event.x_root, event.y_root)

        link.props.points = goocanvas.Points([link.props.points.coords[0], coords2])
        link.raise_(None)

        return False

    def _stopDrag(self, view, pad, event, link):
        "attaches or destroys a link when user lets go of mouse"
        self.logger.debug("stopping drag")
        assert(pad == view == link.get_data("pad"))

        self.destroyLink(link)
        handlers = link.get_data("handlers")
        while len(handlers):
            view.disconnect(handlers.pop())
        #if it's over a pad, try to connect
        #otherwise, destroy the link
        (x, y) = self.get_canvas().convert_from_item_space(pad, event.x, event.y)
        sinkPad = self.get_canvas().get_item_at(x, y, False)
        srcPad = pad.get_parent()
        if sinkPad and sinkPad.get_parent():
            sinkPad = sinkPad.get_parent()
            if sinkPad.get_parent().__class__ == Pad:
                #case of ProxyPad
                srcPad.tryLink(sinkPad.get_parent())
            elif sinkPad.__class__ == Pad:
                srcPad.tryLink(sinkPad)

        self.get_canvas().pointer_ungrab(pad, 0)

        return True
    
    def updateLinks(self):
        for element in self.model.elements():
            element.get_data("widget").updateLinks()
        
        Element.updateLinks(self)
        
    def load(self):
        for child in self.model.elements():
            self.onElementAdded(self.model, child)

class Pipeline(Bin):
    "GooCanvas widget for GStreamer pipeline"
    
    x = 100
    y = 100

    def __init__(self, pipeline):
        Bin.__init__(self, pipeline)
        self.logger.debug("creating gstreamer pipeline")
        #for i in [0,1]:
        #    self.get_child(i).props.visibility = goocanvas.ITEM_INVISIBLE

        self.box.props.fill_color = "blue"
        self.disconnect(self.buttonPressHandler)
        self.disconnect(self.buttonReleaseHandler)
        
    def setSize(self, width, height):
        Bin.setSize(self, width, height)
        if self.get_canvas():
            bounds = self.get_bounds()
            self.get_canvas().set_bounds(bounds.x1 - self.xPadding,
                                         bounds.y1 - self.yPadding,
                                         bounds.x2 + self.xPadding,
                                         bounds.y2 + self.yPadding)