#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA

# GDM2Setup 
#     by Garth Johnson (growlf@BioCEDE.com)
#     original code by Nick Glynn (exosyst@gmail.com)  
#     A simple setup for GDM2, now that Ubuntu seems to be missing this functionality due
#     to omissions within the newer Gnome version included in Ubuntu Karmic and others.
#

import gtk
import os

###TODO: replace all gconf calls with python-gconf support after the access issue is resolved with it.
### This is a temporary kludge that will be replaced as soon as the solution is available.
### ...for now, we must continue to use os.Popen calls to indirectly bypass issues with Orbit/Gconf
from gdm2.gdm2gconf import GDM2Theme


class GDM2Setup(object):    
    
    def on_icontheme_combobox_changed(self, widget, data=None):
        self.theme.SetLoginIconTheme(widget.get_active_text())
    
    def on_gtktheme_combobox_changed(self, widget, data=None):
        self.theme.SetLoginGTKTheme(widget.get_active_text())
        
    def on_blur_checkbutton_toggled(self, widget, data=None):
        BlurLoginImage = widget.get_active()
        if BlurLoginImage:
            WallpaperLocation = self.theme.GetWallpaper()
            self.theme.SetWallpaper(WallpaperLocation, BlurLoginImage)
            self.update_preview()
            widget.queue_draw()
                    
    def on_showloginscreen_radiobutton_toggled(self, widget, data=None):
        # Switch active focus between auto and list options
        self.builder.get_object('autologin_combobox').set_sensitive(False) 
        self.builder.get_object('userlist_checkbutton').set_sensitive(True)   
        # Set the conf
        self.theme.SetAutoLogin(False)

    def on_autologin_radiobutton_toggled(self, widget, data=None):
        # Switch active focus between auto and list options
        self.builder.get_object('userlist_checkbutton').set_sensitive(False) 
        userlist_cb = self.builder.get_object('autologin_combobox')
        userlist_cb.set_sensitive(True) 
        if not userlist_cb.get_active_text():
            userlist_cb.set_active(0)          
        # Set the conf
        self.theme.SetAutoLogin(True, userlist_cb.get_active_text())

    def on_userlist_checkbutton_toggled(self, widget, data=None):
        self.theme.SetShowUserList(widget.get_active())

    def on_autologin_combobox_changed(self, widget, data=None):
        self.theme.SetAutoLogin(True, widget.get_active_text())
               
    def on_disablebuttons_checkbutton_toggled(self, widget, data=None):
        self.theme.SetShowButtons(widget.get_active())
    
    def on_help_clicked(self, widget):
        ###TODO: add in a quick help window.
        print "This function is not yet implemented."

    def on_playsound_checkbutton_toggled(self, widget, data=None):
        self.theme.SetLoginSound(widget.get_active())

    def on_open_wallpaperchooser(self, widget, data=None):
        response = self.chooser.run()
        if response == gtk.RESPONSE_OK: 
            WallpaperLocation = self.chooser.get_filename()
            if os.path.isfile(WallpaperLocation):
                self.theme.SetWallpaper(WallpaperLocation, False)
                self.update_preview()
                widget.queue_draw()
                        
        self.chooser.hide()
        #self.chooser.destroy()

    def on_mainwindow_destroy(self, widget, data=None):
        gtk.main_quit()

    def update_preview(self):
            WallpaperLocation = self.theme.GetWallpaper()
            if os.path.isfile(WallpaperLocation): #If it aint there, don't use it
                self.PreviewThumb.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(WallpaperLocation).scale_simple(250,250,gtk.gdk.INTERP_BILINEAR))
            self.PreviewThumb.queue_draw()

    def add_cbx_entries(self, values, cbxobj, default=None):
        itemcount = 0        
        for v in values:
            cbxobj.append_text(v)
            if v == default:
                cbxobj.set_active(itemcount)
            itemcount += 1
    
    def __init__(self): 
        self.theme = GDM2Theme()
        self.builder = gtk.Builder()

        # Find our cwd and gladefile  
        whereami = os.path.dirname (os.path.abspath (os.path.realpath (__file__)))
        self.builder.add_from_file(os.path.join(whereami, "gdm2setup.glade"))

        # Setup main window
        self.window = self.builder.get_object("mainwindow")
                    
        # Build the GTKThemes combobox entries and attach them
        self.add_cbx_entries(self.theme.GetGTKThemes(),
                             self.builder.get_object('gtktheme_combobox'), 
                             self.theme.GetLoginGTKTheme())
            
        # Build the IconThemes combobox entries
        self.add_cbx_entries(self.theme.GetIconThemes(),
                             self.builder.get_object('icontheme_combobox'), 
                             self.theme.GetLoginIconTheme())
            
        # Build the UserList combobox entries
        self.add_cbx_entries(self.theme.GetAvailableUsers(),
                             self.builder.get_object('autologin_combobox'), 
                             self.theme.GetAutoLoginUser())
        
        # Set Autologin status and associated buttons
        if self.theme.GetAutoLogin():
            self.builder.get_object("autologin_radiobutton").set_active(True)
            self.builder.get_object("autologin_combobox").set_sensitive(True) 
            self.builder.get_object("userlist_checkbutton").set_sensitive(False) 
        else:  
            self.builder.get_object("showloginscreen_radiobutton").set_active(True)
            self.builder.get_object("autologin_combobox").set_sensitive(False) 
            self.builder.get_object("userlist_checkbutton").set_sensitive(True) 
            self.builder.get_object("userlist_checkbutton").set_active(self.theme.GetShowUserList()) 

        # Set the preview image to the current 
        self.PreviewThumb = self.builder.get_object('wallpaper_image')
        self.update_preview()
        
        # Set the status of the login sound option
        playsound_cb = self.builder.get_object('playsound_checkbutton')
        playsound_cb.set_active(self.theme.GetLoginSound())
        
        show_buttons_cb = self.builder.get_object('disablebuttons_checkbutton')
        show_buttons_cb.set_active( self.theme.GetShowButtons())

        ###TODO: move this to the glade file and call with the following line
        #self.chooser = self.builder.get_object('wallpaperchooser_dlg')
        self.chooser = gtk.FileChooserDialog("Select Wallpaper...", None,
                                             gtk.FILE_CHOOSER_ACTION_OPEN,
                                             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = self.builder.get_object('imagefilter')
        filter.set_name("Images")
        filter.add_pattern("*.bmp")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.jpeg")
        filter.add_pattern("*.gif")
        filter.add_pattern("*.png")
        self.chooser.add_filter(filter)

        # connect the callback signal handlers
        self.builder.connect_signals(self)

##########


if __name__ == "__main__":
    ###TODO: check that xsplash IS installed - for some reason it is not always there
    if os.geteuid() != 0:
        dlg = gtk.Dialog("GDM2 Setup", None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                      (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dlg.set_border_width(10)
        dlg.vbox.set_border_width(10)
        dlgLabel = gtk.Label("This program needs to be run as root.\nTry again with using either\nsudo or gksudo")
        dlgLabel.set_justify(gtk.JUSTIFY_CENTER)
        dlgLabel.set_line_wrap(True)
        dlg.vbox.pack_start(dlgLabel)
        dlg.show_all()
        dlgResult = dlg.run()
        dlg.destroy()
    else:
        # Start the app up
        app = GDM2Setup()
        app.window.show()
        gtk.main()
