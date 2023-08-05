"""
    utils.py
    Fri Jun 14 13:41:56 2004
    Copyright  2005 Italian Python User Group
    http://www.italianpug.org
   
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Library General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import gtk

class Combo(gtk.ComboBox):
    def __init__(self):
        gtk.ComboBox.__init__(self)
        renderer = gtk.CellRendererText()
        self.pack_start(renderer)
        self.add_attribute(renderer, 'text', 0)

    def set_model(self, model):
        gtk.ComboBox.set_model(self, model)
        if len(model) == 1:
            self.set_active(0)
    
def make_text(widget):
    """
    Return a scrolled window with a given widget inside
    @param widget: The widget tu put inside the scrolled window
    @return: ScrolledWindow
    """
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.set_border_width(2)
    sw.set_shadow_type(gtk.SHADOW_IN)
    sw.add(widget)
    widget.show()
    return sw
    
def make_button(text, stock):
    """
    Make a button specifying its text label and stock icon
    @param label: The text of the button
    @param stock: Personalized stock item
    @return: Button
    """
    btn = gtk.Button()
    align = gtk.Alignment(0.5, 0.5)
    hbox = gtk.HBox(spacing=2)
    img = gtk.Image()
    img.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
    hbox.pack_start(img, 0)
    label = gtk.Label()
    label.set_markup(text)
    hbox.pack_start(label, 0)
    align.add(hbox)
    btn.add(align)
    return btn
