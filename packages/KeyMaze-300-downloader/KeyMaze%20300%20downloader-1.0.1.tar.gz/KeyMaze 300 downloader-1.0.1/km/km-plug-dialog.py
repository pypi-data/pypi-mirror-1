#!/usr/bin/python
#Python script to download trackpoints and waypoints form a KeyMaze 300 GPS.
    #Copyright (C) 2008  Julien TOUS

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pygtk
pygtk.require('2.0')

import gobject
import gtk
import gtk.glade

class km_plug_dialog:
        
        def __init__(self):
                self.gladefile = ""/usr"/share/km/km-plug-dialog.glade"
                self.wTree = gtk.glade.XML(self.gladefile)
                self.window = self.wTree.get_widget("km_plug_dialog_window")
                self.window.show_all()
	        #Create our dictionay and connect it
	        dic = { "on_cancel_button_clicked" : self.close,
	                "on_close_button_clicked" : self.set_device_and_close, 
                        "on_km_plug_dialog_window_close" : self.set_device_and_close 
                        }
	        self.wTree.signal_autoconnect(dic)

        def set_device_and_close(self,dummy):
                print "KeyMaze300"
                gtk.main_quit()
                #quit()

        def close(self,dummy):
                gtk.main_quit()
                #quit()


if __name__ == '__main__':
        #debug = open('~/km.debug','w')
        #debug.write('km-plu-dialog was launched !')
        #debug.close()
        plug_dialog = km_plug_dialog()
        gtk.main()
