"""
    translation.py
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

import gtk, thread, os
from utils import *

class TranslationBase:
    def on_module(self, widget):
        """
        Get the Translator class then insert from languages using the language table
        and set w_from widget sensitive.
        """
        itr = self.w_module.get_active_iter()
        self.translator = self.w_module.get_model().get_value(itr, 1)(self._parent)
        from_langs = []
        from_model = gtk.ListStore(str)
        for lang in self.translator.language_table:
            if lang["from"] not in from_langs:
                from_langs.append(lang["from"])
                from_model.append([lang["from"]])
        if self.translator.language_table:
            self.w_from.set_model(from_model)
            self.w_from.set_sensitive(1)
        try:
            if not self.custom_tab_name:
                self.tab_name = widget.get_active_text()
                self.set_label_tab()
            if self.translator.icon_file:
                self.tab_image.set_from_file(os.path.join(self._parent.icons, self.translator.icon_file))
        except: pass

    
    def on_from(self, widget):
        """
        Get the languages which can be translated from the selected language
        and set w_to widget sensitive.
        """
        self.translator.from_lang = widget.get_active_text()
        to_model = gtk.ListStore(str)
        for lang in self.translator.language_table:
            if lang["from"] == widget.get_active_text():
                to_model.append([lang["to"]])

        self.w_to.set_model(to_model)
        if len(to_model) == 1:
            self.w_to.set_active(0)
        self.w_to.set_sensitive(1)
    
    def on_to(self, widget):
        """
        Translation ready to be started
        """
        self.translator.to_lang = widget.get_active_text()
        self.w_translate.set_sensitive(1)
        
class Translation(gtk.Frame, TranslationBase):
    def __init__(self, parent, preferred):
        """
        Create a new empty translation page
        """
        gtk.Frame.__init__(self)
        self._parent = parent
        self.translating = 0
        self.set_border_width(3)
        
        vbox = gtk.VBox(spacing=3)
        hbox = gtk.HBox(spacing=3)
        
        hbox.pack_start(gtk.Label(_('Translation:')), 0, 0)
        self.w_module = self._parent.make_combo_modules()
        hbox.pack_start(self.w_module)
        
        hbox.pack_start(gtk.Label(_('From:')), 0, 0)
        self.w_from = Combo()
        self.w_from.set_sensitive(0)
        hbox.pack_start(self.w_from)
        
        hbox.pack_start(gtk.Label(_('To:')), 0, 0)
        self.w_to = Combo()
        self.w_to.set_sensitive(0)
        hbox.pack_start(self.w_to)
     
        self.w_translate = make_button(_('<u>T</u>ranslate!'), gtk.STOCK_REFRESH)
        self.w_translate.set_sensitive(0)
        hbox.pack_start(self.w_translate, 0, 0)
        vbox.pack_start(hbox, 0, 0)

        buffer = gtk.TextBuffer() 
        if self._parent.config.getboolean('clipboard', 'get') and self._parent.clipboard.wait_is_text_available():
            text = self._parent.clipboard.wait_for_text()
            if text != self._parent.cur_clipboard:
                buffer.paste_clipboard(self._parent.clipboard, None, 1)
                self._parent.cur_clipboard = text
                self._parent.clipboard.clear()
        self.w_textfrom = gtk.TextView(buffer)
        vbox.pack_start(make_text(self.w_textfrom))
        vbox.pack_start(gtk.HSeparator(), 0, 0)
        self.w_textto = gtk.TextView()
        vbox.pack_start(make_text(self.w_textto))
        
        self.w_module.connect("changed", self.on_module)
        self.w_from.connect("changed", self.on_from)
        self.w_to.connect("changed", self.on_to)
        self.w_translate.connect("clicked", self.on_translate)
        accel = gtk.AccelGroup()
        self.w_translate.add_accelerator('clicked', accel, ord('T'), gtk.gdk.CONTROL_MASK, 0)
        self._parent.add_accel_group(accel)
        self.add(vbox)
        
        self.tab_name = 'Unnamed'
        self.custom_tab_name = 0
        self.tab = gtk.HBox(spacing=3)
        self.tab_event = gtk.EventBox()
        self.tab_event.connect('button-press-event', self.on_tab_pressed)
        self.tab_label = gtk.Label()
        self.tab_entry = gtk.Entry()
        self.tab_entry.connect('changed', self.on_tab_changed)
        self.tab_entry.connect('activate', self.on_tab_renamed)
        self.tab_event.add(self.tab_label)
        self.set_label_tab()
        self.tab_image = gtk.Image()
        self.tab.pack_start(self.tab_image)
        self.tab.pack_start(self.tab_event)

        self.tab_menu = gtk.Menu()
        
        item = gtk.ImageMenuItem(gtk.STOCK_EDIT, _('Rename'))
        item.connect('button-press-event', self.on_tab_renaming)
        self.tab_menu.add(item)
        
        item = gtk.ImageMenuItem(gtk.STOCK_CLOSE, _('Close'))
        item.connect('button-press-event', self.on_close)
        
        self.tab_menu.add(item)
        self.tab_menu.show_all()
        
        if preferred: self._parent.preferred_combo_module(self.w_module)
        
        close = gtk.Button()
        close.set_relief(gtk.RELIEF_NONE)
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close.add(img)
        close.connect('clicked', self.on_close)
        self.tab.pack_start(close)
        self.tab.show_all()
        self.tab_image.show()
        self.show_all()
        
    # Tools
    
    def translate(self, text):
        """
        Set all widgets insinsitive and start translation.
        After this view the new translated text and let widgets be sensitive.
        @param text: Text to be translated
        """
        self.translating = 1
        widgets = [self.w_translate, self.w_module, self.w_from, self.w_to, self.w_textfrom]
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(0)
            gtk.threads_leave()
        translated = self.translator.translate(text)
        gtk.threads_enter()
        buffer = gtk.TextBuffer()
        buffer.set_text(translated)
        self.w_textto.set_buffer(buffer)
        if self._parent.config.getboolean('clipboard', 'set'):
            self._parent.clipboard.set_text(translated)
            self._parent.cur_clipboard = translated
        gtk.threads_leave()
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(1)
            gtk.threads_leave()
        self.translating = 0
        gtk.threads_enter()
        nb = self._parent.nb
        if nb.get_nth_page(nb.get_current_page()) != self:
            self.tab_label.set_markup('<span color="blue">'+
                                      self.tab_name+'</span>') 
        gtk.threads_leave()
            
    def set_label_tab(self):
        self.tab_event.remove(self.tab_event.get_child())
        self.tab_event.add(self.tab_label)
        self.tab_label.set_text(self.tab_name)
        self.tab_label.show()
        
    def set_entry_tab(self):
        self.tab_event.remove(self.tab_event.get_child())
        self.tab_entry.set_text(self.tab_name)
        self.tab_entry.set_width_chars(len(self.tab_name))
        self.tab_entry.show()
        self.tab_event.add(self.tab_entry)
        
    def start_tab_renaming(self):
        self.set_entry_tab()
        self.custom_tab_name = 1
        
    # Events
              
    def on_translate(self, widget):
        """
        Start the translation by spawning a new thread
        """
        buffer = self.w_textfrom.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        if not text: return
        thread.start_new_thread(self.translate, (text,))
        
    def on_close(self, *w):
        """
        Remove myself from the notebook.
        Don't care if a translation is running on.
        """
        if self.translating and self._parent.question(_('A translation is currently running. Are you sure to close this page?')) == gtk.RESPONSE_YES or not self.translating:
            self._parent.nb.remove(self)
            
    def on_tab_pressed(self, w, event):
        """
        Mouse pressed on the tab
        """
        if event.button == 1:
            if event.type == gtk.gdk.BUTTON_PRESS:
                self.tab_label.set_text(self.tab_name)
            elif event.type == gtk.gdk._2BUTTON_PRESS:
                self.start_tab_renaming()
        elif event.button == 3:
            self.tab_menu.popup(None, None, None, 0, event.time)
        
    def on_tab_renamed(self, w):
        """
        The tab as been renamed
        """
        self.set_label_tab()

    def on_tab_changed(self, w):
        self.tab_name = w.get_text()
        self.tab_entry.set_width_chars(len(self.tab_name))
        
    def on_tab_renaming(self, w, event):
        if event.button == 1: self.start_tab_renaming()

class MiniTranslation(gtk.Window, TranslationBase):
    class Popup(gtk.Dialog):
        def __init__(self, parent, text, translated):
            gtk.Dialog.__init__(self, 'FreeSpeak - '+_('Translation'), parent, 0,
                    (gtk.STOCK_CLOSE, gtk.RESPONSE_OK))
            self.set_position(gtk.WIN_POS_CENTER)
            self.set_border_width(3)
            self.set_resizable(1)
            self.vbox.set_spacing(3)

            label = gtk.Label()
            label.set_markup(_('From')+
                    ' <b>'+parent.w_from.get_active_text()+'</b> '+
                    _('to')+
                    ' <b>'+parent.w_to.get_active_text()+'</b> '+
                    _('using')+
                    ' <b>'+parent.w_module.get_active_text()+'</b>')
            label.show()
            self.vbox.pack_start(label, 0, 0)
            
            w_text = gtk.TextView()
            w_text.get_buffer().set_text(text)
            w_text.set_sensitive(0)
            scroll = make_text(w_text)
            scroll.show()
            self.vbox.pack_start(scroll)
            
            w_text = gtk.TextView()
            w_text.get_buffer().set_text(translated)
            w_text.set_sensitive(0)
            scroll = make_text(w_text)
            scroll.show()
            self.vbox.pack_start(scroll)
            
    def __init__(self, parent):
        gtk.Window.__init__(self)
        self.set_title('FreeSpeak')
        
        self.connect('show', self.on_show)
        self._parent = parent
        self.translating = 0
        self.set_keep_above(1)
        self.set_icon(self._parent.get_icon())

        self.update_trayicon_settings()

        hbox = gtk.HBox(spacing=3)
        
        button = make_button('', gtk.STOCK_CONVERT)
        button.connect('clicked', self.on_normalize)
        hbox.pack_start(button, 0, 0)
        self.w_module = self._parent.make_combo_modules()
        hbox.pack_start(self.w_module)
        
        self.w_from = Combo()
        self.w_from.set_sensitive(0)
        hbox.pack_start(self.w_from)
        
        self.w_to = Combo()
        self.w_to.set_sensitive(0)
        hbox.pack_start(self.w_to)
     
        self.w_translate = make_button('', gtk.STOCK_REFRESH)
        self.w_translate.set_sensitive(0)
        hbox.pack_start(self.w_translate, 0, 0)
        
        self.w_module.connect("changed", self.on_module)
        self.w_from.connect("changed", self.on_from)
        self.w_to.connect("changed", self.on_to)
        self.w_translate.connect("clicked", self.on_translate)
        accel = gtk.AccelGroup()
        self.w_translate.add_accelerator('clicked', accel, ord('T'), gtk.gdk.CONTROL_MASK, 0)

        self._parent.add_accel_group(accel)
        
        self.add(hbox)
        

    def translate(self, text):
        """
        Set all widgets insinsitive and start translation.
        After this view the new translated text and let widgets be sensitive.
        @param text: Text to be translated
        """
        self.translating = 1
        widgets = [self.w_translate, self.w_module, self.w_from, self.w_to]
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(0)
            gtk.threads_leave()
        translated = self.translator.translate(text)
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(1)
            gtk.threads_leave()
        if not self.translating: return
        gtk.threads_enter()
        if self._parent.config.getboolean('minimalist', 'popup') or not self._parent.config.getboolean('clipboard', 'set'):
            popup = MiniTranslation.Popup(self, text, translated)
            popup.run()
            popup.destroy()
        if self._parent.config.getboolean('clipboard', 'set'):
            self._parent.clipboard.set_text(translated)
            self._parent.cur_clipboard = translated
        gtk.threads_leave()
        self.translating = 0
        
    def update_trayicon_settings(self):
        if self._parent.tray:
            try:
                self.disconnect(self.h_destroy)
            except: pass
            self.h_delete = self.connect('delete-event', self.on_delete)
        else:
            try:
                self.disconnect(self.h_delete)
            except: pass
            self.h_destroy = self.connect('destroy',
                                          lambda *w: gtk.main_quit())  
        
    # Events
    
    def on_normalize(self, w):
        if self.translating and self._parent.question(_('A translation is currently running. Are you sure to close this page?')) == gtk.RESPONSE_YES or not self.translating:
            self.translating = 0
            self.hide()
            self._parent.show_all()
            self._parent.is_reduced = 0
            
    def on_translate(self, w):
        if self._parent.clipboard.wait_is_text_available():
            text = self._parent.clipboard.wait_for_text()
            if not text: return
            self._parent.clipboard.clear()
            thread.start_new_thread(self.translate, (text,))
            
    def on_show(self, w):
        self._parent.preferred_combo_module(self.w_module)

    def on_delete(self, w, Data=None):
        self._parent.tray.wnd_hide()
        return True
