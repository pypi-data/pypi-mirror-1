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

import gtk, sys, thread, time
from contactlist import ContactList
from history import History
import gtk.gdk as gdk

class BaseSend:
    def __init__(self, p, state):
        self.p, self.state, self.cancel = p, state, 0
        
    def error(self, msg):
        self.p.p.error(msg, self.p)
        
    def __call__(self, fraction=0, text=''):
        gtk.threads_enter()
        self.state['bar'].set_fraction(fraction)
        self.state['bar'].set_text(text)
        gtk.threads_leave()

    def run(self, *calls):
        self.p.w_send.set_sensitive(0)
        thread.start_new_thread(self.run_thread, calls)
    
    def run_thread(self, *calls):
        for call in calls:
            if self.cancel: break
            while 1:
                try: call()
                except:
                    if self.cancel: break
                    gtk.threads_enter()
                    res = self.p.p.question("""An error was occurred while sending the sms to %s:
    
    %s
    
    Whould you like to retry?""" % (self.phone, sys.exc_value), 0, self.p)
                    gtk.threads_leave()
                    if res == gtk.RESPONSE_YES: continue
                    else: self.cancel = 1
                break
        self.end(self.cancel)
                
    def end(self, error=0):
        self.state['state'] = 0
        clear = 1
        for state in self.p.states:
            if state['state']: clear = 0
        if not error:
            if clear:
                gtk.threads_enter()
                self.p.buf.set_text('')
                gtk.threads_leave()
            self(1, 'Message sent successful')
        else: self(0, 'Cancelled!')
        gtk.threads_enter()
        if clear: self.p.w_send.set_sensitive(1)
        self.state['cancel'].set_sensitive(0)
        self.p.p.pop()
        gtk.threads_leave()
        
class Send(gtk.Window):
    def __init__(self, p, sms, provider, username, password, phone='', text=''):
        gtk.Window.__init__(self)
        self.p = p
        self.username = username
        self.password = password
        self.sms = sms
        self.provider = provider
        
        self.set_title('pyWebSMS - '+self.provider)
        self.set_border_width(3)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(1)
        
        vbox = gtk.VBox(spacing=3)
        
        # Contact and phone
        hbox = gtk.HBox(spacing=3)
        
        btn = self.p.button('Contact', gtk.STOCK_INDEX)
        btn.connect('clicked', self.on_contact)
        hbox.pack_start(btn, 0)
        
        self.w_phone = gtk.Entry()
        self.w_phone.set_text(phone)
        hbox.pack_start(self.w_phone)
        vbox.pack_start(hbox, 0)
        
        # Text area
        self.buf = gtk.TextBuffer()
        self.buf.set_text(text)
        self.w_text = gtk.TextView(self.buf)
        self.w_text.set_wrap_mode(gtk.WRAP_CHAR)
        self.buf.connect('changed', self.on_text)
        scroll = self.p.scroll(self.w_text)
        vbox.pack_start(scroll)
        
        hbox = gtk.HBox(spacing=3)
        hbox.set_border_width(3)
        
        # History
        self.history = {}
        btn = self.p.button('History', gtk.STOCK_JUSTIFY_FILL)
        btn.connect('clicked', self.on_history)
        hbox.pack_start(btn, 0)
        hbox.pack_start(gtk.VSeparator(), 0)
        
        # Char count
        hbox.pack_start(gtk.Label('Characters left: '), 0)
        self.w_chars = gtk.Entry()
        self.w_chars.set_sensitive(0)
        self.w_chars.set_text(str(self.sms.max_chars-len(text)))
        self.w_chars.set_size_request(len(str(self.sms.max_chars))*10, -1)
        hbox.pack_start(self.w_chars, 0)
        
        hbox.pack_start(gtk.Label('of'), 0)
        chars = gtk.Entry()
        chars.set_sensitive(0)
        chars.set_text(str(self.sms.max_chars))
        chars.set_size_request(len(str(self.sms.max_chars))*10, -1)
        hbox.pack_start(chars, 0)
        vbox.pack_start(hbox, 0)
        
        # State
        vbox.pack_start(gtk.HSeparator(), 0)
        self.states = []
        self.exp = gtk.Expander('State')
        vbox.pack_start(self.exp, 0)
        
        # Buttons
        vbox.pack_start(gtk.HSeparator(), 0)
        hbox = gtk.HButtonBox()
        hbox.set_layout(gtk.BUTTONBOX_SPREAD)
        hbox.set_border_width(3)
        hbox.set_spacing(3)
        
        self.w_send = self.p.button('Send', gtk.STOCK_OK)
        self.w_send.connect('clicked', self.on_send)
        hbox.pack_start(self.w_send)
        
        self.w_clear = gtk.Button(stock=gtk.STOCK_CLEAR)
        self.w_clear.connect('clicked', self.on_clear)
        hbox.pack_start(self.w_clear)
        
        self.w_close = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.w_close.connect('clicked', self.on_close)
        hbox.pack_start(self.w_close)
        vbox.pack_start(hbox, 0)
        
        self.add(vbox)
        self.show_all()
        
    # Functions
    def get_sms(self):
        return self.buf.get_text(self.buf.get_start_iter(), self.buf.get_end_iter())
        
    # Events
    def on_send(self, w):
        phones = [p.strip() for p in self.w_phone.get_text().split(';')]
        try: self.table.destroy()
        except: pass
        self.table = gtk.Table(len(phones), 3)
        self.table.set_col_spacings(3)
        self.exp.add(self.table)
        for phone, row in zip(phones, range(len(phones))):
            state = {
                'row': row,
                'label': gtk.Label(phone),
                'bar': gtk.ProgressBar(),
                'state': 1
            }
            self.history[time.time()] = [phone, self.get_sms()]
            base = BaseSend(self, state)
            base.username = self.username
            base.password = self.password
            base.phone = phone
            base.text = self.get_sms()
            sms = self.sms(base)
            base.sms = sms
            cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
            cancel.connect('clicked', self.on_cancel, base)
            state['cancel'] = cancel
            if not sms.start(): return
            self.p.push()
            for w, col in zip(('label', 'bar', 'cancel'), range(3)):
                self.table.attach(state[w], col, col+1, row, row+1)
            self.table.show_all()
            self.states.append(state)
        
    def on_close(self, w):
        self.destroy()
        
    def on_text(self, w):
        if w.get_char_count() > self.sms.max_chars:
            w.delete(w.get_iter_at_offset(w.get_char_count()-1), w.get_end_iter())
        self.w_chars.set_text(str(self.sms.max_chars-w.get_char_count()))
        
    def on_clear(self, w):
        self.w_phone.set_text('')
        self.buf.set_text('')
        states = []
        for state in self.states:
            if state['state']: states.append(state)
        self.exp.remove(self.table)
        self.table = gtk.Table(len(states)+1, 3)
        for state, row in zip(states, range(len(states))):
            for w, col in zip(('label', 'bar', 'cancel'), range(3)):
                state[w].unparent()
                self.table.attach(state[w], col, col+1, row, row+1)
        self.table.show_all()
        self.exp.add(self.table)
        self.states = states
        
    def on_contact(self, w):
        phones = ContactList(self).start()
        if phones: self.w_phone.set_text(phones)
        
    def on_cancel(self, w, base):
        base.cancel = 1
        w.set_sensitive(0)

    def on_history(self, w):
        History(self)
