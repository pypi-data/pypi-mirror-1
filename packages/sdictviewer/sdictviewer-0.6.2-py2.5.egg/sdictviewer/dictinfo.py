"""
This file is part of SDict Viewer (http://sdictviewer.sf.net) - 
a dictionary application that allows to use data bases 
in AXMASoft's open dictionary format. 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2006-2008 Igor Tkach
"""
import pygtk
pygtk.require('2.0')
import gtk, pango, locale, ui

class DictDetailPane(gtk.HBox):
    
    def __init__(self):
        super(DictDetailPane, self).__init__()
        self.lbl_title = self.create_value_label()
        self.lbl_version = self.create_value_label()
        self.lbl_copyright = self.create_value_label()
        self.lbl_file_name = self.create_value_label()
        self.lbl_compression = self.create_value_label()
        self.lbl_num_of_words = self.create_value_label()
        table = gtk.Table(6, 2, False)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add_with_viewport(table)                                
        
        self.pack_start(scrolled_window, True, True, 0)
        #self.pack_start(table, True, True, 0)
        table.set_row_spacings(5)
        table.set_col_spacings(5)
        table.attach(self.create_label("Title:"),0,1,0,1, xoptions = gtk.FILL, yoptions = gtk.FILL)
        table.attach(self.lbl_title,1,2,0,1, xoptions = gtk.FILL | gtk.EXPAND, yoptions = gtk.FILL)
        table.attach(self.create_label("Version:"),0,1,1,2, xoptions = gtk.FILL, yoptions = gtk.FILL)
        table.attach(self.lbl_version,1,2,1,2, yoptions = 0)        
        table.attach(self.create_label("Copyright:"),0,1,2,3, xoptions = gtk.FILL, yoptions = gtk.FILL)
        table.attach(self.lbl_copyright,1,2,2,3, yoptions = gtk.FILL)                
        table.attach(self.create_label("Articles:"),0,1,3,4, xoptions = gtk.FILL, yoptions = gtk.FILL)
        table.attach(self.lbl_num_of_words,1,2,3,4, yoptions = gtk.FILL)                        
        table.attach(self.create_label("From file:"),0,1,4,5, xoptions = gtk.FILL, yoptions = gtk.FILL)
        table.attach(self.lbl_file_name,1,2,4,5, yoptions = gtk.FILL)                                
        table.attach(self.create_label("Compression:"),0,1,5,6, xoptions = gtk.FILL, yoptions = gtk.FILL)
        table.attach(self.lbl_compression,1,2,5,6)                                
        table.set_border_width(5)
            
    def create_label(self, text):
        lbl = gtk.Label(text)
        lbl.set_alignment(1.0, 0.0)
        return lbl
    
    def create_value_label(self):
        lbl = gtk.Label()
        lbl.set_alignment(0.0, 0.0)
        lbl.set_line_wrap(True)
        return lbl
    
    
    def set_dict(self, dict):
        if dict:
            self.lbl_title.set_text(dict.title)
            self.lbl_version.set_text(dict.version)
            self.lbl_copyright.set_text(dict.copyright)
            self.lbl_num_of_words.set_text(locale.format("%d", dict.header.num_of_words))
            self.lbl_file_name.set_text(dict.file_name)
            self.lbl_compression.set_text("%s" % dict.compression)
        else:
            self.lbl_title.set_text('')
            self.lbl_version.set_text('')
            self.lbl_copyright.set_text('')
            self.lbl_num_of_words.set_text('')                     
            self.lbl_file_name.set_text('')   
            self.lbl_compression.set_text('')
        
        
class DictInfoDialog(gtk.Dialog):
    def __init__(self, dicts, parent):        
        super(DictInfoDialog, self).__init__(title="Dictionary Info", flags=gtk.DIALOG_MODAL, parent = parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.add_button(gtk.STOCK_CLOSE, 1)
        self.connect("response", lambda w, resp: w.destroy())
                        
        contentBox = self.get_child()
        box = gtk.VBox(contentBox)        
                
        dict_list = gtk.TreeView(gtk.ListStore(object))
        cell = gtk.CellRendererText()
        dict_column = gtk.TreeViewColumn('Dictionary', cell)
        dict_list.append_column(dict_column)
        dict_column.set_cell_data_func(cell, self.extract_dict_title_for_cell)
        
        for dict in dicts:
            dict_list.get_model().append([dict])
                
        box.pack_start(ui.create_scrolled_window(dict_list), True, True, 0)

        split_pane = gtk.HPaned()        
        contentBox.pack_start(split_pane, True, True, 2)                        
        split_pane.add(box)
        
        self.detail_pane = DictDetailPane()
        
        split_pane.add(self.detail_pane)
        split_pane.set_position(200)
                    
        dict_list.get_selection().connect("changed", self.dict_selected)
        self.resize(600, 320)
        self.show_all()
                                        
        
    def extract_dict_title_for_cell(self, column, cell_renderer, model, iter, data = None):
        dict = model[iter][0]
        cell_renderer.set_property('text', dict.title)
        return        
    
    def dict_selected(self, selection):
        dict = None
        if selection.count_selected_rows() > 0:
            model, iter = selection.get_selected()
            dict = model[iter][0]
        self.detail_pane.set_dict(dict)
