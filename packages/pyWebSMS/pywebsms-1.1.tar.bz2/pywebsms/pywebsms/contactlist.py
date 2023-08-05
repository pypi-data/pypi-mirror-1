############################################################################
#    Copyright (C) 2004 by Lethalman                                       #
#    lethalman@fyrebird.net                                                #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import gtk

class ContactList(gtk.Dialog):
    def __init__(self, p):
        gtk.Dialog.__init__(self, 'pyWebSMS - Contact', p, 0,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.p = p
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(3)
        self.resize(200, 300)
        
        self.vbox.set_spacing(3)
        
        # Contact list
        self.model = gtk.ListStore(str, str)
        self.list = gtk.TreeView(self.model)
        self.list.set_rules_hint(1)
        self.list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.list.connect('row-activated', lambda *w: self.response(gtk.RESPONSE_OK))
        for col, n in zip(('Name', 'Phone'), range(2)):
            column = gtk.TreeViewColumn(col, gtk.CellRendererText(), text=n)
            column.set_resizable(1)
            column.set_sort_column_id(n)
            self.list.append_column(column)
        self.vbox.pack_start(self.p.p.scroll(self.list))
        
    def start(self):
        self.show_all()
        page = self.p.p.pages[1]
        itr = page.model.get_iter_first()
        data = []
        while itr:
            self.model.append(page.model.get(itr, 0, 1))
            itr = page.model.iter_next(itr)
        while 1:
            if self.run() == gtk.RESPONSE_OK:
                for path in self.list.get_selection().get_selected_rows()[1]:
                    data.append(self.model.get_value(self.model.iter_nth_child(None, path[0]), 1))
                if data: break
            else: break
        self.destroy()
        return '; '.join(data)
