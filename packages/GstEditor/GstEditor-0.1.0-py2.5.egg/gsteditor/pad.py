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

import goocanvas
import logging
import gst

class Pad(goocanvas.Group):
    """Represents gstreamer pad"""

    minSize = 3
    radius = 4

    def __init__(self, pad):
        goocanvas.Group.__init__(self)
        self.widget = goocanvas.Ellipse(radius_x = self.radius,
                                        radius_y = self.radius,
                                        fill_color = "blue",
                                        line_width = 2,
                                        stroke_color = "black")
        self.add_child(self.widget)
        self.model = pad
        self.link = None

        self.logger = logging.getLogger(self.model.get_name()) 
        self.model.set_data("widget", self)

        self.widget.props.tooltip = self.model.get_name()

        #pads sometimes links before adding to element, so we can't use this signals
        self.model.connect("linked", self.onLinked)
        self.model.connect("unlinked", self.onUnlinked)

    def onLinked(self, pad1, pad2):
        self.logger.debug("linked. pad1=" + str(pad1) + " pad2=" + str(pad2))
        assert(pad1 == self.model)
        #first try to take existing link from peer
        peer = pad2.get_data("widget")
        if peer:
            if peer.link:
                self.link = peer.link
            else:
                #creating new link
                peer.link = self.link = self.get_parent().get_parent().makeLink(self, peer)
        else:
            ghostPad = pad2.get_parent()
            #check that it is really ghost pad
            if ghostPad.__class__ == gst.GhostPad:
                #if peer is ProxyPad then use it's parent - GhostPad
                if not ghostPad.get_parent():
                    self.logger.warning("no parent for pad " + str(ghostPad) + "- delaying signal handler")
                    ghostPad.set_data("link-handler", lambda: self.onLinked(pad1, pad2))
                else:
                    #peer = ghostPad.get_data("widget")
                    #making widget for ProxyPad
                    peer = Pad(pad2)
                    ghostPad.get_data("widget").add_child(peer)
                    self.link = peer.get_parent().get_parent().makeLink(self, peer)
                    self.link.props.line_dash = goocanvas.LineDash([3.0])
            else:
                self.logger.warning("no widget for pad " + str(pad2) + "- delaying signal handler")
                pad2.set_data("link-handler", lambda: self.onLinked(pad1, pad2))

    def onUnlinked(self, pad1, pad2):
        logging.debug("unlinked. pad1=" + str(pad1) + " pad2=" + str(pad2))
        assert(pad1 == self.model)
        assert(pad2.get_parent().__class__ == gst.GhostPad or pad2.get_data("widget").link == self.link or not pad2.get_data("widget").link)
        self.link.get_parent().destroyLink(self.link)
        self.link = None
        
    def tryLink(self, peer):
        if self.model.can_link(peer.model):
            if peer.model.get_direction() == gst.PAD_SRC:
                peer.model.link(self.model)
            else:
                self.model.link(peer.model)

            self.onLinked(self.model, peer.model)
            peer.onLinked(peer.model, self.model)
            #TODO: tidy up the link drawing so that the endpoint is
            #      orthogonal and ends at the radius

    def updateLink(self):
        #make link widget for linked pads
        if self.model.is_linked():
            self.onLinked(self.model, self.model.get_peer())
            
    def setPosition(self, x, y):
        self.set_simple_transform(x, y, 1, 0)