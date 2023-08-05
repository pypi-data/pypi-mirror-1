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

import gtk, os

class Provider(gtk.Dialog):
    def __init__(self, p, name='', module='', username='', password=''):
        gtk.Dialog.__init__(self, 'pyWebSMS - Provider', p.p, 0,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.p = p
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(3)
        
        self.vbox.set_spacing(3)
        table = gtk.Table(5, 2)
        table.set_border_width(3)
        table.set_row_spacings(3)
        table.set_col_spacings(3)
        
        table.attach(gtk.Label('Name:'), 0, 1, 0, 1)
        self.w_name = gtk.Entry()
        self.w_name.set_text(name)
        table.attach(self.w_name, 1, 2, 0, 1)
        
        table.attach(gtk.Label('Module:'), 0, 1, 1, 2)
        self.w_module = gtk.ComboBox(gtk.ListStore(str))
        table.attach(self.w_module, 1, 2, 1, 2)
        
        table.attach(gtk.HSeparator(), 0, 2, 2, 3)
        
        table.attach(gtk.Label('Username:'), 0, 1, 3, 4)
        self.w_username = gtk.Entry()
        self.w_username.set_text(username)
        table.attach(self.w_username, 1, 2, 3, 4)
        
        table.attach(gtk.Label('Password:'), 0, 1, 4, 5)
        self.w_password = gtk.Entry()
        self.w_password.set_text(password)
        table.attach(self.w_password, 1, 2, 4, 5)
        
        self.vbox.pack_start(table)
        
        modules = filter(lambda x: x[0]!='_' and os.path.isdir('providers'+os.sep+x),
                os.listdir('providers'))
        renderer = gtk.CellRendererText()
        self.w_module.set_model(gtk.ListStore(str))
        self.w_module.pack_start(renderer)
        self.w_module.add_attribute(renderer, 'text', 0)
        for mod in modules:
            if not self.p.p.get_module(mod): continue
            self.w_module.append_text(mod)
        model = self.w_module.get_model()
        select = itr = model.get_iter_first()
        while itr:
            if model.get_value(itr, 0) == module: select = itr
            itr = model.iter_next(itr)
        if select: self.w_module.set_active_iter(select)
               
    def start(self, add=1):
        if not self.w_module.get_active_text():
            return self.p.p.error('No suitable protocols were found!')
        self.show_all()
        data = {}
        while 1:
            if self.run() == gtk.RESPONSE_OK:
                provider = self.w_name.get_text()
                if not provider: continue
                if add and self.p.p.check_dup(self.p.model, provider, 0): continue
                for w in 'name', 'username', 'password':
                    data[w] = getattr(self, 'w_'+w).get_text()
                data['module'] = self.w_module.get_active_text()
            break
        self.destroy()
        return data
