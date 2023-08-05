"""
    settings.py
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

import gtk, gtk.gdk, os.path
#from src.utils import *

class Settings(gtk.Dialog):
    def __init__(self, parent):
        """
        FreeSpeak user preferences
        """
        gtk.Dialog.__init__(self, 'FreeSpeak - '+_('Settings'), parent, 0,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self._parent = parent
        config = parent.config
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(3)
        self.vbox.set_spacing(3)
        
        frame = gtk.Frame(_('Clipboard preferences'))
        frame.set_border_width(3)
        vbox = gtk.VBox(spacing=3)
        
        self.w_clipboard_get = gtk.CheckButton(_('Get text from clipboard automatically'))
        self.w_clipboard_get.set_active(config.getboolean('clipboard', 'get'))
        vbox.pack_start(self.w_clipboard_get, 0, 0)
        self.w_clipboard_set = gtk.CheckButton(_('Save text to clipboard after translation'))
        self.w_clipboard_set.set_active(config.getboolean('clipboard', 'set'))
        vbox.pack_start(self.w_clipboard_set, 0, 0)
        
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)

        frame = gtk.Frame(_("Translator preferences"))
        frame.set_border_width(3)
        vbox = gtk.VBox(spacing=3)
        
        hbox = gtk.HBox(spacing=3)
        hbox.pack_start(gtk.Label(_("Preferred Translator")), 0 ,0)
        self.w_preferred_translator = self._parent.make_combo_modules()
        
        preferred_translator = self._parent.config.get("translator", "preferred")     
        for row in self.w_preferred_translator.get_model():
            if row[0] == preferred_translator:
                self.w_preferred_translator.set_active_iter(row.iter)
        hbox.pack_start(self.w_preferred_translator, 1 ,1)
        vbox.pack_start(hbox)
        
        self.w_always_top = gtk.CheckButton(_('Keep translator always on top'))
        self.w_always_top.set_active(config.getboolean('translator', 'alwaysontop'))
        vbox.pack_start(self.w_always_top)
        
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)
        
        frame = gtk.Frame(_('Minimalist translator preferences'))
        frame.set_border_width(3)
        vbox = gtk.VBox(spacing=3)
        
        self.w_mini_startup = gtk.CheckButton(_('Startup with minimalist translator window'))
        self.w_mini_startup.set_active(config.getboolean('minimalist', 'startup'))
        vbox.pack_start(self.w_mini_startup)
        
        self.w_mini_popup = gtk.CheckButton(_('Show translated text in a popup window'))
        self.w_mini_popup.set_active(config.getboolean('minimalist', 'popup'))
        self.w_clipboard_set.connect('toggled', self.on_sensitive, self.w_mini_popup, 'minimalist', 'popup')
        if not self.w_clipboard_set.get_active():
            self.w_mini_popup.set_active(1)
            self.w_mini_popup.set_sensitive(0)
        else: self.w_mini_popup.set_active(config.getboolean('minimalist', 'popup'))
        vbox.pack_start(self.w_mini_popup)
        
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)


        frame = gtk.Frame(_('Interface preferences'))
        frame.set_border_width(3)
        hbox = gtk.HBox(spacing=3)

        hbox.pack_start(gtk.Label(_("Language")),0 ,0)
        self.w_language = gtk.ComboBox()
        text = gtk.CellRendererText()
        icon = gtk.CellRendererPixbuf()
        self.w_language.pack_start(icon, 0)
        self.w_language.pack_start(text)
        self.w_language.add_attribute(text, 'text', 0)
        self.w_language.set_cell_data_func(icon, self.load_icon) 
        language_model = gtk.ListStore(str) #(gtk.gdk.Pixbuf)
        language_model.append(["System Default"])
        
        for language in self._parent.locale.get_list():
            try:
                language_model.append([language])
            except: pass
        self.w_language.set_model(language_model)
            
        language = self._parent.config.get("interface", "language")     
        for row in self.w_language.get_model():
            if row[0] == language:
                self.w_language.set_active_iter(row.iter)

        hbox.pack_start(self.w_language, 1, 1)
      
        frame.add(hbox)
        frame.show_all()
        self.vbox.pack_start(frame)


        frame = gtk.Frame(_('Miscellaneous preferences'))
        frame.set_border_width(3)
        vbox = gtk.VBox(spacing=3)
        
        self.w_trayicon = gtk.CheckButton(_('Use Tray Icon'))
        self.w_trayicon.set_active(config.getboolean('miscellaneous',
        'trayicon'))
        vbox.pack_start(self.w_trayicon)
      
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)

    def load_icon(self, celllayout, cell, model, iter, user_data=None):
        try:
            icon = "%s%s%s.png" % (self._parent.icons, os.path.sep, model.get_value(iter, 0))
            pixbuf= gtk.gdk.pixbuf_new_from_file(icon)
            cell.set_property('pixbuf', pixbuf)
        except: pass
        return
    
    def start(self):
        if self.run() == gtk.RESPONSE_CANCEL:
            self.destroy()
            return
        config = self._parent.config
        def checkbox(widget, section, value):
            if widget.get_active(): config.set(section, value, 'yes')
            else: config.set(section, value, 'no')
        # Clipboard
        checkbox(self.w_clipboard_get, 'clipboard', 'get')
        checkbox(self.w_clipboard_set, 'clipboard', 'set')
        # Translator
        config.set("translator", "preferred",
                   self.w_preferred_translator.get_active_text())
        checkbox(self.w_always_top, 'translator', 'alwaysontop')
        self._parent.set_keep_above(self.w_always_top.get_active())
        # Minimalist
        checkbox(self.w_mini_startup, 'minimalist', 'startup')
        if self.w_mini_popup.get_property('sensitive'):
            checkbox(self.w_mini_popup, 'minimalist', 'popup')
        # Interface
        if config.get("interface", "language") != \
               self.w_language.get_active_text():
            w_dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL,
                                         gtk.MESSAGE_INFO,
                                         gtk.BUTTONS_OK,
                                         _("Restart FreeSpeak to apply language changes")
                                         )
            if w_dialog.run():
                w_dialog.destroy()
        config.set("interface", "language", self.w_language.get_active_text())
        
        # Miscellaneous
        checkbox(self.w_trayicon, 'miscellaneous', 'trayicon')
        if self.w_trayicon.get_active():
            try:
                self._parent.create_trayicon()
            except: pass
        else:
            self._parent.remove_trayicon()
        self._parent.reduced.update_trayicon_settings()
        
        config.save()
        self.destroy()
    
    # Events
    
    def on_sensitive(self, w1, w2, section, option):
        if w1.get_active():
            w2.set_sensitive(1)
            w2.set_active(self._parent.config.getboolean(section, option))
        else:
            w2.set_sensitive(0)
            w2.set_active(1)
