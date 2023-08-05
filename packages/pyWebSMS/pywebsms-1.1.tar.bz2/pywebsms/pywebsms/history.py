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

import gtk, time

class History(gtk.Window):
    def __init__(self, p):
        gtk.Window.__init__(self)
        self.p = p
        
        self.set_title('pyWebSMS - History')
        self.set_border_width(3)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(1)
        
        hbox = gtk.HBox(spacing=3)

        # History
        self.model = gtk.ListStore(str, str, str, float)
        self.list = gtk.TreeView(self.model)
        self.list.set_rules_hint(1)
        self.list.connect('row-activated', lambda *w: self.on_view())
        for col, n in zip(('Phone', 'SMS Text', 'Date'), range(3)):
            column = gtk.TreeViewColumn(col, gtk.CellRendererText(), text=n)
            column.set_resizable(1)
            column.set_sort_column_id(n)
            self.list.append_column(column)
        for t in sorted(self.p.history.keys()):
            text = self.p.history[t][1]
            if len(text) > 15: text = text[:15]+'...'
            self.model.append((self.p.history[t][0], text, time.ctime(t), t))
        scroll = self.p.p.scroll(self.list)
        scroll.set_size_request(350, 200)
        hbox.pack_start(scroll)
        
        # Buttons
        box = gtk.VButtonBox()
        box.set_layout(gtk.BUTTONBOX_START)
        box.set_border_width(3)
        box.set_spacing(3)
        btn = gtk.Button(stock=gtk.STOCK_REMOVE)
        btn.connect('clicked', self.on_remove)
        box.pack_start(btn, 0)
        btn = self.p.p.button('View', gtk.STOCK_JUSTIFY_FILL)
        btn.connect('clicked', self.on_view)
        box.pack_start(btn, 0)
        btn = gtk.Button(stock=gtk.STOCK_CLOSE)
        btn.connect('clicked', lambda *w: self.destroy())
        box.pack_start(btn, 0)
        hbox.pack_start(box, 0)
        
        self.add(hbox)
        self.show_all()
    
    def get_selected(self):
        return self.list.get_selection().get_selected()[1]

    def on_view(self, *w):
        itr = self.get_selected()
        if not itr: return
        t = self.model.get_value(itr, 3)
        send = self.p.__class__(self.p.p, self.p.sms, self.p.provider, self.p.username, self.p.password,
                self.p.history[t][0], self.p.history[t][1])
       
    def on_remove(self, w):
        itr = self.get_selected()
        if not itr: return
        t = self.model.get_value(itr, 3)
        self.model.remove(itr)
        del self.p.history[t]
