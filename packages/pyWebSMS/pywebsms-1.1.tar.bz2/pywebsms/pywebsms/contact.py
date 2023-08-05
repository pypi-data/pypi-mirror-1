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

class Contact(gtk.Dialog):
    def __init__(self, p, name='', phone='', real='', address='', other=''):
        gtk.Dialog.__init__(self, 'pyWebSMS - Contact', p.p, 0,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.p = p
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(3)
        
        self.vbox.set_spacing(3)
        table = gtk.Table(6, 2)
        table.set_border_width(3)
        table.set_row_spacings(3)
        table.set_col_spacings(3)
        
        table.attach(gtk.Label('Name:'), 0, 1, 0, 1)
        self.w_name = gtk.Entry()
        self.w_name.set_text(name)
        table.attach(self.w_name, 1, 2, 0, 1)
        
        table.attach(gtk.Label('Phone:'), 0, 1, 1, 2)
        self.w_phone = gtk.Entry()
        self.w_phone.set_text(phone)
        table.attach(self.w_phone, 1, 2, 1, 2)
        
        table.attach(gtk.HSeparator(), 0, 2, 2, 3)
        
        table.attach(gtk.Label('Real name:'), 0, 1, 3, 4)
        self.w_real = gtk.Entry()
        self.w_real.set_text(real)
        table.attach(self.w_real, 1, 2, 3, 4)
        
        table.attach(gtk.Label('Address:'), 0, 1, 4, 5)
        self.w_address = gtk.Entry()
        self.w_address.set_text(address)
        table.attach(self.w_address, 1, 2, 4, 5)
        
        table.attach(gtk.Label('Other:'), 0, 1, 5, 6)
        self.w_other = gtk.Entry()
        self.w_other.set_text(other)
        table.attach(self.w_other, 1, 2, 5, 6)
        
        self.vbox.pack_start(table)
        
    def start(self, add=1):
        self.show_all()
        data = {}
        while 1:
            if self.run() == gtk.RESPONSE_OK:
                contact = self.w_name.get_text()
                phone = self.w_phone.get_text()
                if not contact or not phone: continue
                if add and self.p.p.check_dup(self.p.model, phone, 1): continue
                for w in 'name', 'phone', 'real', 'address', 'other':
                    data[w] = getattr(self, 'w_'+w).get_text()
            break
        self.destroy()
        return data
