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
from gtk.gdk import CONTROL_MASK as control
from provider import Provider
from contact import Contact
from config import Config
from send import Send

class Page(gtk.Frame):
    def __init__(self, p):
        gtk.Frame.__init__(self)
        self.p = p
        self.set_border_width(3)
        
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        
        # Data list
        self.model = gtk.TreeStore(str, str)
        self.list = gtk.TreeView(self.model)
        self.list.set_rules_hint(1)
        for col, n in zip(('Name', 'Informations'), range(2)):
            column = gtk.TreeViewColumn(col, gtk.CellRendererText(), text=n)
            column.set_resizable(1)
            column.set_sort_column_id(n)
            self.list.append_column(column)
        hbox.pack_start(self.p.scroll(self.list))
        
        # Right button box
        self.buttons = gtk.VButtonBox()
        self.buttons.set_layout(gtk.BUTTONBOX_START)
        self.buttons.set_border_width(3)
        self.buttons.set_spacing(3)
        hbox.pack_start(self.buttons, 0)
        vbox.pack_start(hbox)
        
        # File entry
        hbox = gtk.HBox(spacing=3)
        
        hbox.pack_start(gtk.Label('Current file:'), 0, 0)
        self.w_file = gtk.Entry()
        self.w_file.set_editable(0)
        hbox.pack_start(self.w_file)
        vbox.pack_start(hbox, 0)
        
        self.add(vbox)
        
    def get_selected(self):
        model, itr = self.list.get_selection().get_selected()
        if itr and not model.iter_parent(itr): return itr    
        
    def save(self):
        if not self.conf.file: return self.p.on_saveas()
        self.conf.save()
        
    def changed(self):
        if self.conf.changed:
            res = self.p.question('Whould you like to save changes to %s?' % self.__class__.__name__)
            if res == gtk.RESPONSE_CANCEL: return 1
            elif res == gtk.RESPONSE_YES: self.save()
            
    def file(self, f):
        self.w_file.set_text(f)
        self.conf.file = f
        
class Providers(Page):
    def __init__(self, p):
        Page.__init__(self, p)
        
        btn = gtk.Button(stock=gtk.STOCK_ADD)
        btn.connect('clicked', self.on_add)
        btn.add_accelerator('clicked', self.p.accel, ord('A'), control, 0)     
        self.buttons.pack_start(btn, 0)
        
        btn = gtk.Button(stock=gtk.STOCK_REMOVE)
        btn.connect('clicked', self.on_remove)
        btn.add_accelerator('clicked', self.p.accel, ord('R'), control, 0)     
        self.buttons.pack_start(btn, 0)
        
        btn = gtk.Button(stock=gtk.STOCK_EDIT)
        btn.add_accelerator('clicked', self.p.accel, ord('E'), control, 0)     
        btn.connect('clicked', self.on_edit)
        self.buttons.pack_start(btn, 0)
        
        btn = self.p.button('Send', gtk.STOCK_OK)
        btn.connect('clicked', self.on_send)
        self.buttons.pack_start(btn, 0)
        
        self.list.connect('row-activated', lambda *w: self.on_send())
        
        # Configuration
        self.sms = {}
        self.conf = Config()
        self.file(self.p.config.get('Defaults', 'lastprv'))
        self.load()
        
    def save(self):
        self.p.setpage(0)
        Page.save(self)
        
    def load(self):
        self.model.clear()
        self.conf.load()
        for name in self.conf.sections():
            module = self.conf.get(name, 'module')
            self.sms[name] = self.p.get_module(module)
            itr = self.model.append(None, [name, module])
            for i in 'Username', 'Password':
                self.model.append(itr, [i, self.conf.get(name, i.lower())])
        self.conf.changed = 0
        
    def default(self):
        self.p.config.set('Defaults', 'lastprv', self.conf.file)
        
    def on_add(self, w):
        data = Provider(self).start()
        if not data: return
        self.conf.add_section(data['name'])
        self.conf.set(data['name'], 'module', data['module'])
        itr = self.model.append(None, [data['name'], data['module']])
        for i in 'username', 'password':
            self.model.append(itr, [i.capitalize(), data[i]])
            self.conf.set(data['name'], i, data[i])
        self.sms[data['name']] = self.p.get_module(data['module'])
            
    def on_remove(self, w):
        itr = self.get_selected()
        if not itr: return
        name = self.model.get_value(itr, 0)
        self.conf.remove_section(name)
        del self.sms[name]
        self.model.remove(itr)
        
    def on_edit(self, w):
        itr = self.get_selected()
        if not itr: return
        opts = {}
        opts['name'], opts['module'] = self.model.get(itr, 0, 1)
        citr = self.model.iter_children(itr)
        while citr:
            k, v = self.model.get(citr, 0, 1)
            opts[k.lower()] = v
            citr = self.model.iter_next(citr)
        data = Provider(self, **opts).start(0)
        if not data: return
        self.conf.rename_section(opts['name'], data['name'])
        self.conf.set(data['name'], 'module', data['module'])
        self.model.set(itr, 0, data['name'], 1, data['module'])
        self.sms[data['name']] = self.sms[opts['name']]
        del self.sms[opts['name']]
        citr = self.model.iter_children(itr)
        while citr:
            k = self.model.get_value(citr, 0).lower()
            self.conf.set(data['name'], k, data[k])
            self.model.set(citr, 1, data[k])
            citr = self.model.iter_next(citr)
            
    def on_send(self, *w):
        itr = self.get_selected()
        if not itr: return
        name = self.model.get_value(itr, 0)
        provider = self.sms[name]
        if not provider: return self.p.error("This provider doesn't seem to work properly")
        Send(self.p, provider, name,
                self.conf.get(name, 'username'), self.conf.get(name, 'password'))

class Contacts(Page):
    def __init__(self, p):
        Page.__init__(self, p)
        
        btn = gtk.Button(stock=gtk.STOCK_ADD)
        btn.connect('clicked', self.on_add)
        btn.add_accelerator('clicked', self.p.accel, ord('A'), control, 0)     
        self.buttons.pack_start(btn, 0)
        
        btn = gtk.Button(stock=gtk.STOCK_REMOVE)
        btn.connect('clicked', self.on_remove)
        btn.add_accelerator('clicked', self.p.accel, ord('R'), control, 0)     
        self.buttons.pack_start(btn, 0)
        
        btn = gtk.Button(stock=gtk.STOCK_EDIT)
        btn.connect('clicked', self.on_edit)
        btn.add_accelerator('clicked', self.p.accel, ord('E'), control, 0)     
        self.buttons.pack_start(btn, 0)
        
        self.list.connect('row-activated', lambda *w: self.on_edit())
        
        # Configuration
        self.conf = Config()
        self.file(self.p.config.get('Defaults', 'lastcts'))
        self.load()
        
    def save(self):
        self.p.setpage(1)
        Page.save(self)
        
    def load(self):
        self.model.clear()
        self.conf.load()
        for phone in self.conf.sections():
            name = self.conf.get(phone, 'name')
            itr = self.model.append(None, [name,phone])
            for i in 'Real name', 'Address', 'Other':
                self.model.append(itr, [i, self.conf.get(phone, i.split(' ')[0].lower())])
        self.conf.changed = 0
        
    def default(self):
        self.p.config.set('Defaults', 'lastcts', self.conf.file)
        
    def on_add(self, w):
        data = Contact(self).start()
        if not data: return
        self.conf.add_section(data['phone'])
        self.conf.set(data['phone'], 'name', data['name'])
        itr = self.model.append(None, [data['name'], data['phone']])
        for i in 'Real name', 'Address', 'Other':
            key = i.split(' ')[0].lower()
            self.model.append(itr, [i, data[key]])
            self.conf.set(data['phone'], key, data[key])

    def on_remove(self, w):
        itr = self.get_selected()
        if not itr: return
        name = self.model.get_value(itr, 0)
        res = self.p.question('Whould you like remove %s?' % name, 0)
        if res == gtk.RESPONSE_YES:
            self.conf.remove_section(name)
            self.model.remove(itr)
        
    def on_edit(self, *w):
        itr = self.get_selected()
        if not itr: return
        opts = {}
        opts['name'], opts['phone'] = self.model.get(itr, 0, 1)
        citr = self.model.iter_children(itr)
        while citr:
            k, v = self.model.get(citr, 0, 1)
            opts[k.split(' ')[0].lower()] = v
            citr = self.model.iter_next(citr)
        data = Contact(self, **opts).start(0)
        if not data: return
        self.conf.rename_section(opts['phone'], data['phone'])
        self.model.set(itr, 0, data['name'], 1, data['phone'])
        citr = self.model.iter_children(itr)
        while citr:
            k = self.model.get_value(citr, 0).split(' ')[0].lower()
            self.conf.set(data['phone'], k, data[k])
            self.model.set(citr, 1, data[k])
            citr = self.model.iter_next(citr)
