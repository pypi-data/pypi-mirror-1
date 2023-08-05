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

from ConfigParser import ConfigParser

class Config(ConfigParser):
    def __init__(self, file=None, autowrite=0):
        ConfigParser.__init__(self)
        self.file = file
        self.autowrite = autowrite
        self.changed = 0
        
    def get(self, section, option):
        try: return ConfigParser.get(self, section, option)
        except: return ''
        
    def save(self):
        self.write(open(self.file, 'w'))
        self.changed = 0
        
    def load(self, clear=1):
        if clear: self.clear()
        try: self.readfp(open(self.file))
        except: pass
        self.changed = 0
        
    def clear(self):
        for section in self.sections(): self.remove_section(section)
        self.changed = 0
        
    def rename_section(self, old, new):
        if old == new: return
        self.add_section(new)
        for k, v in self.items(old): self.set(new, k, v)
        self.remove_section(old)
        self.changed = 1
        if self.autowrite: self.save()
    
    def add_section(self, *args):
        ConfigParser.add_section(self, *args)
        self.changed = 1
        if self.autowrite: self.save()
        
    def remove_section(self, *args):
        ConfigParser.remove_section(self, *args)
        self.changed = 1
        if self.autowrite: self.save()
        
    def set(self, *args):
        ConfigParser.set(self, *args)
        self.changed = 1
        if self.autowrite: self.save()
