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


import gtk
import gobject

class ParamWin(gtk.Window):
    """this class provides a convenient Gtk+ widget that will pop open a
    non-modal window with widgets to control and adjust the parameters for
    any Gstreamer Element.  The module was designed as part of the Gstreamer
    Graphical Pipeline Editor."""
    
    def __init__(self, element=None):
        gtk.Window.__init__(self)
        
        if element:
            title = element.props.name + " - Parameters"
            self.set_title(title)
            self.element = element
            
        self.set_position(gtk.WIN_POS_MOUSE)
        self.set_default_size(500, 600)

        self.connect("delete-event", self.onDelete)
        self.connect("show", self.onShow)
        
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(15)
        self.scrollwin = gtk.ScrolledWindow()
        self.scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrollwin.add_with_viewport(self.vbox)
        self.add(self.scrollwin)
        
        #TODO: make this prettier
        self.vbox.pack_start(gtk.Label('Set Element Parameters'), expand=False, padding=10)
        
        proplist = gobject.list_properties(self.element)
        self.table = gtk.Table(len(proplist), 3)
        self.table.props.row_spacing = 5
        self.table.props.column_spacing = 5
        self.vbox.pack_start(self.table, expand=False, padding=10)
        
        #here we will hold ***Prop objects
        self.props = list()
        
        count = 0
        for property in proplist:
            label = gtk.Label(property.name)
            label.set_alignment(1, 0.5)
            label.set_tooltip_text(property.blurb)
            self.table.attach(label, 0, 1, count, count+1)
            
            prop = None

            #non readable params
            if not(property.flags & gobject.PARAM_READABLE):
                rlabel = gtk.Label("-parameter not readable-")
                self.table.attach(rlabel, 1, 2, count, count+1)

            # just display non-writable param values
            elif not(property.flags & gobject.PARAM_WRITABLE):
                try:
                    wvalue = self.element.get_property(property.name)
                    if wvalue:
                        wlabel = gtk.Label(wvalue)
                        self.table.attach(wlabel, 1, 2, count, count+1)
                except:
                    self.table.attach(gtk.Label("-can't read parameter-"), 1, 2, count, count+1)
            
            elif hasattr(property, "minimum") and hasattr(property, "maximum"):
                prop = AdjustmentProp(self.element, property)
                self.table.attach(prop.widget, 1, 2, count, count+1)
                
            elif gobject.type_is_a(property.value_type, gobject.TYPE_BOOLEAN):
                prop = BooleanProp(self.element, property)
                self.table.attach(prop.widget, 1, 2, count, count+1)

            elif hasattr(property, "enum_class"):
                prop = EnumProp(self.element, property)
                self.table.attach(prop.widget, 1, 2, count, count+1)

            elif gobject.type_is_a(property.value_type, gobject.TYPE_STRING):
                prop = StringProp(self.element, property)
                self.table.attach(prop.widget, 1, 2, count, count+1)

            if property.flags & gobject.PARAM_WRITABLE and property.flags & gobject.PARAM_READABLE and prop != None:
                defbutton = gtk.Button("Default")
                defbutton.connect("clicked", lambda button, prop: prop.SetDefault(), prop)
                self.table.attach(defbutton, 2, 3, count, count+1)
                
            if prop != None:
                self.props.append(prop)
            
            count += 1
            #TODO: sort out how best to clean up signal handlers

    def onDelete(self, window, event):
        "Hide the window when the user closes it"
        self.hide()
        return True
    
    def onShow(self, window):
        "Update all property values"
        for prop in self.props:
            prop.Update()
    
class BaseProp:
    "Base class for property and widget holders"
    def __init__(self, element, property):
        self.element = element
        self.property = property
        
    def SetDefault(self):
        "Set property value to default and update widget"
        self.element.set_property(self.property.name, self.property.default_value)
        self.Update()

class AdjustmentProp(BaseProp):
    def __init__(self, element, property):
        BaseProp.__init__(self, element, property)
        adj = gtk.Adjustment(0, property.minimum, property.maximum, 1, 10)
        
        adj.connect("value_changed", self._on_changed)
        
        if property.maximum - property.minimum > 20:
            self.widget = gtk.SpinButton(adj)
            
        else:
            self.widget = gtk.HScale(adj)
            self.widget.set_value_pos(gtk.POS_RIGHT)
            
            #check for ints and change digits
            if not((property.value_type == gobject.TYPE_FLOAT) or
                    (property.value_type == gobject.TYPE_DOUBLE)):
                self.widget.set_digits(0)
        
    def _on_changed(self, adj):      
        "Update element parameter when slider is moved or number is spinned"
        #cast non float types as int
        if not(self.property.value_type == gobject.TYPE_FLOAT or
               self.property.value_type == gobject.TYPE_DOUBLE):
            value = int(adj.get_value())
        else:
            value = adj.get_value()

        self.element.set_property(self.property.name, value)
        return True
        
    def Update(self):
        self.widget.set_value(self.element.get_property(self.property.name))

class BooleanProp(BaseProp):
    def __init__(self, element, property):
        BaseProp.__init__(self, element, property)
        
        #booleans get a toggle button
        self.widget = gtk.CheckButton()
        self.widget.connect("toggled", self._on_toggled)

    def _on_toggled(self, button):
        "Update element boolean parameter when button is toggled"
        tstate = button.get_active()
        self.element.set_property(self.property.name, tstate)
        return True
    
    def Update(self):
        "Update widget with property value"
        self.widget.set_active(self.element.get_property(self.property.name))

class EnumProp(BaseProp):
    "This class represents enum_class property and holds GTK ComboBox"
    def __init__(self, element, property):
        BaseProp.__init__(self, element, property)
    
        #for enumerated types, use a combobox
        choices = _getChoices(property)
        
        self.widget = gtk.ComboBox(choices)
        cell = gtk.CellRendererText()
        self.widget.pack_start(cell, True)
        self.widget.add_attribute(cell, 'text', 0)
        self.widget.connect("changed", self._on_changed)
        
    def _on_changed(self, widget):
        "Change element parameter when the ComboBox value is adjusted"
        model = self.widget.get_model()
        iter = self.widget.get_active_iter()
    
        #we need to grab the actual enum value for non-serial values
        enum = model.get_value(iter, 1)
        self.element.set_property(self.property.name, enum)
        
    def Update(self):
        "Update selection accordingly to current property value"
        self.widget.set_active(self.element.get_property(self.property.name))

class StringProp(BaseProp):
    "This class represents string property and holds GTK Entry widget"
    def __init__(self, element, property):
        BaseProp.__init__(self, element, property)
        
        #strings get a gtk.Entry widget
        self.widget = gtk.Entry()        
        self.widget.connect("changed", self._on_changed)
        
    def _on_changed(self, widget):
        "update text parameter"
        self.element.set_property(self.property.name, self.widget.get_text())
        
    def Update(self):
        "Update text accordingly to current property value"
        text = self.element.get_property(self.property.name)
        # ignore empty strings
        if text:
            self.widget.set_text(text)


def _getChoices(cls):
    """This method is a slightly modified version of the EnumType handler 
    from Gazpacho (http://gazpacho.sicem.biz/) as written by Johan Dahlin 
    (jdahlin@async.com.br).  It returns a sorted gtk.ListStore of columns with 
    the form: (name string, enum int value)"""
    
    choices = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    if not hasattr(cls.enum_class, '__enum_values__'):
        raise UnsupportedProperty

    for enum in cls.enum_class.__enum_values__.values():
        choices.append((enum.value_name, enum))
    choices.set_sort_column_id(1, gtk.SORT_ASCENDING)
    return choices
