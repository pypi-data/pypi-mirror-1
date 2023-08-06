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
               
    def on_enabletimededlogin_checkbutton_toggled(self, widget, data=None):
        ###TODO: enable this
        print "on_enabletimededlogin_checkbutton_toggled: ", widget.get_active()
    
    def on_timedlogin_cbx_changed(self, widget, data=None):
        ###TODO: enable this
        print "timedlogin_cbx_changed_cb: ", widget.get_active()
        
    def on_disablebuttons_checkbutton_toggled(self, widget, data=None):
        self.theme.SetShowButtons(widget.get_active())
        
    def on_banner_checkbutton_toggled(self, widget, data=None):
        banner = self.builder.get_object('banner_entry')
        if widget.get_active():
            banner.set_sensitive(True)
        else:
            banner.set_sensitive(False)
        self.theme.SetBannerEnable(widget.get_active())
    
    def on_banner_entry_activate(self, widget, data=None):
        self.theme.SetBanner(widget.get_text())
    
    def on_about_button_clicked(self, widget, data=None):
        response = self.about.run()
        print response == gtk.RESPONSE_CLOSE
            
    # Any response from an 'about' dialog is a 'close' - so just close it
    def on_gdm2setup_aboutdialog_response(self, widget, data=None):
        widget.hide()
 
    # Enable or disable the login sounds
    def on_playsound_checkbutton_toggled(self, widget, data=None):
        self.theme.SetLoginSound(widget.get_active())

    # This is clicked from the main dialog to open the file chooser dialog
    def on_open_wallpaperchooser(self, widget, data=None):
        response = self.chooser.run()
        if response == gtk.RESPONSE_OK: 
            WallpaperLocation = self.chooser.get_filename()
            if os.path.isfile(WallpaperLocation):
                self.theme.SetWallpaper(WallpaperLocation, False)
                self.update_preview()
                widget.queue_draw()
        self.chooser.hide()
        
    # Manage the preview updates
    def on_wallpaperchooser_dlg_update_preview(self, widget, data=None):
        WallpaperLocation = self.chooser.get_filename()
        if WallpaperLocation:
            if os.path.isfile(WallpaperLocation):
				try:
					preview = self.builder.get_object('previewimage')
					preview.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(WallpaperLocation).scale_simple(100,100,gtk.gdk.INTERP_BILINEAR))
					preview.queue_draw()
				except:
					return

    # This is clicked from the wallpaper chooser dialog
    def on_openwallpaper_bn_clicked(self, widget, data=None):
        self.chooser.response(gtk.RESPONSE_OK)
        
    # This is clicked from the wallpaper chooser dialog
    def on_cancelwallpaper_bn_clicked(self, widget, data=None):
        self.chooser.response(gtk.RESPONSE_CANCEL)

    # This updates the wallpaper preview in the main dialog
    def update_preview(self):
        WallpaperLocation = self.theme.GetWallpaper()
        if os.path.isfile(WallpaperLocation):
			try:
				self.PreviewThumb.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(WallpaperLocation).scale_simple(250,250,gtk.gdk.INTERP_BILINEAR))
			except:
				# Bad file?
				return 
        self.PreviewThumb.queue_draw()

    # create entries for generic combo-box controls
    def add_cbx_entries(self, values, cbxobj, default=None):
        itemcount = 0        
        for v in values:
            cbxobj.append_text(v)
            if v == default:
                cbxobj.set_active(itemcount)
            itemcount += 1
    
    def on_mainwindow_destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self): 
        self.theme = GDM2Theme()
        self.builder = gtk.Builder()

        # Find our cwd and ui file  
        whereami = os.path.dirname (os.path.abspath (os.path.realpath (__file__)))
        self.builder.add_from_file(os.path.join(whereami, "gdm2setup.ui"))

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
            
        banner = self.builder.get_object("banner_entry")
        banner_checkbutton = self.builder.get_object("banner_checkbutton")
        banner.set_text(self.theme.GetBannerText())
        if self.theme.GetBannerEnable():
            banner.set_sensitive(True)
            banner_checkbutton.set_active(True)
        else:
            banner.set_sensitive(False)
            banner_checkbutton.set_active(False)

        # Set the preview image to the current 
        self.PreviewThumb = self.builder.get_object('wallpaper_image')
        self.update_preview()
        
        # Set the status of the login sound option
        playsound_cb = self.builder.get_object('playsound_checkbutton')
        playsound_cb.set_active(self.theme.GetLoginSound())
        
        show_buttons_cb = self.builder.get_object('disablebuttons_checkbutton')
        show_buttons_cb.set_active( self.theme.GetShowButtons())

        # Set the about dialog up
        self.about = self.builder.get_object('gdm2setup_aboutdialog')

        # Create and configure the file chooser dialog
        self.chooser = self.builder.get_object('wallpaperchooser_dlg')
        self.filter = self.builder.get_object('imagefilter')
        self.filter.set_name("Images")
        self.filter.add_pattern("*.bmp")
        self.filter.add_pattern("*.jpg")
        self.filter.add_pattern("*.jpeg")
        self.filter.add_pattern("*.gif")
        self.filter.add_pattern("*.png")
        self.chooser.add_filter(self.filter)

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
