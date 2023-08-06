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
# to omissions within the newer Gnome version included in Karmic Ubuntu and others.
#
# This is GPL2 so fix it and tell us what/where and why

# This file is absorbed from the original gdm-setup by Nick Glynn (exosyst@gmail.com) 
# Rewritten (by growlf@biocede.com) as a class for temporary use in 
# GDM2Setup (at least until gconf/orbit security issues are resolved and we can use
# python-gconf again as other users)
#
# Replaced dependency on ImageMagic with default PIL library calls - *G*
# Replaced directory list code to make it simpler and more consistent -  added sort also - *G*

import subprocess
import os.path
import os
import ImageFilter, Image
import subprocess

class GDM2Theme(object):  
      
    GDMCONF_FILE = u"/etc/gdm/custom.conf"
    THEMES_DIRECTORY = u"/usr/share/themes/"
    ICONS_DIRECTORY = u"/usr/share/icons/"
    XSPLASH_IMAGE = u"/usr/share/images/xsplash/bg.jpg"

    def __init__(self):
        # Lets switch to the GDM user, since that is who all our changes need to take place as
        #os.setuid(pwd.getpwnam( 'gdm' )[2])

        ###FIXME: this fails due to gconf/Orbit security issues

        # Get a gconf instance to work with from GDM
        #self.client = gconf.client_get_default ()
        
        pass

    
    def GetAutoLogin(self):
        if not os.path.isfile(self.GDMCONF_FILE):
            self.SetAutoLogin(False)
            return False
        file = open(self.GDMCONF_FILE,'r')
        index = file.read().find("AutomaticLoginEnable=true")
        AutoLogin = False
        if index > 0:
            AutoLogin=True
        file.close()    
        return AutoLogin
    
    def SetAutoLogin(self, DoIt, User=None):
        file = open(self.GDMCONF_FILE, 'w')
        if DoIt == False:
            file.write("\n[daemon]\nTimedLoginEnable=false\nAutomaticLoginEnable=false\nTimedLogin=\nAutomaticLogin=\nTimedLoginDelay=30\n")
        if DoIt == True and User is not None:
            file.write("\n[daemon]\nTimedLoginEnable=false\nAutomaticLoginEnable=true\nTimedLogin="+User+"\nAutomaticLogin="+User+"\nTimedLoginDelay=30\n")
        file.close()
    
    def GetAutoLoginUser(self):
        ###TODO: get the actual existing value
        if not os.path.isfile(self.GDMCONF_FILE):
            self.SetAutoLogin(False)
            return None
        file = open(self.GDMCONF_FILE,'r')
        
        return None
    
    def GetDirNames(self, dir):
        """ Gets a list of directories and returns them as a cleaned list  """
        dirnames = []
        names = os.listdir(dir)
        for dirname in names:
            path = os.path.join(dir, dirname)
            if os.path.isdir(path):
                dirnames.append(dirname)
        return sorted(dirnames)
    
    def GetGTKThemes(self):
        return self.GetDirNames(self.THEMES_DIRECTORY)
    
    def GetIconThemes(self):
        return self.GetDirNames(self.ICONS_DIRECTORY)

    def SetWallpaper(self, WallpaperLocation, DoBlur):
        """ Sets the wallpaper and performs any mutations the user has requested. """
        
        image = Image.open(WallpaperLocation)
        if DoBlur: 
            image.filter(ImageFilter.BLUR).save(self.XSPLASH_IMAGE)
        else:
            image.save(self.XSPLASH_IMAGE)
            
        ###TODO: this is a hack - we need to actually create the image sizes even though the system will
        ### automatically do it because it introduces some image jumping during it's efforts - looks ugly

        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_800x600.jpg"], stdout=subprocess.PIPE).wait()
        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_1024x768.jpg"], stdout=subprocess.PIPE).wait()
        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_1280x800.jpg"], stdout=subprocess.PIPE).wait()
        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_1280x1024.jpg"], stdout=subprocess.PIPE).wait()
        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_1440x900.jpg"], stdout=subprocess.PIPE).wait()
        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_1680x1050.jpg"], stdout=subprocess.PIPE).wait()
        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_1920x1200.jpg"], stdout=subprocess.PIPE).wait()
        retcall = subprocess.Popen(["ln", "-s", "-f", "-T", "/usr/share/images/xsplash/bg.jpg", "/usr/share/images/xsplash/bg_2560x1600.jpg"], stdout=subprocess.PIPE).wait()
        
    def GetWallpaper(self, ): #This is nigh on useless as the picture is always the same location when we're done with it
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-g", "/desktop/gnome/background/picture_filename"], stdout=subprocess.PIPE)
        return retcall.stdout.readline().strip('\n')
    
    def SetLoginSound(self, MakeNoise):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-s", "/desktop/gnome/sound/event_sounds", "--type", "bool", ('true','false')[not MakeNoise]], stdout=subprocess.PIPE).wait()
    
    def GetLoginSound(self, ):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-g", "/desktop/gnome/sound/event_sounds"], stdout=subprocess.PIPE)
        if 'false' in retcall.stdout.readline():
            return False
        else:
            return True
    
    #These two are backwards as the hide is the special case HURR DURR!
    def SetShowUserList(self, ShowIt):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-s", "/apps/gdm/simple-greeter/disable_user_list", "--type", "bool", ('false', 'true')[not ShowIt]], stdout=subprocess.PIPE).wait()
    
    def GetShowUserList(self, ):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-g", "/apps/gdm/simple-greeter/disable_user_list"], stdout=subprocess.PIPE)
        if 'false' in retcall.stdout.readline():
            return True
        else:
            return False
    
    def SetShowButtons(self, ShowIt):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-s", "/apps/gdm/simple-greeter/disable_restart_buttons", "--type", "bool", ('false', 'true')[ShowIt]], stdout=subprocess.PIPE).wait()
    
    def GetShowButtons(self, ):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-g", "/apps/gdm/simple-greeter/disable_restart_buttons"], stdout=subprocess.PIPE)
        if 'false' in retcall.stdout.readline():
            return False
        else:
            return True
    
    def SetLoginGTKTheme(self, Theme):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-s", "/desktop/gnome/interface/gtk_theme", "--type", "string", Theme], stdout=subprocess.PIPE).wait()
    
    def GetLoginGTKTheme(self, ):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-g", "/desktop/gnome/interface/gtk_theme"], stdout=subprocess.PIPE)
        return retcall.stdout.readline().strip('\n')
    
    def SetLoginIconTheme(self, Theme):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-s", "/desktop/gnome/interface/icon_theme", "--type", "string", Theme], stdout=subprocess.PIPE).wait()
    
    def GetLoginIconTheme(self, ):
        retcall = subprocess.Popen(["sudo", "-u", "gdm", "gconftool-2", "-g", "/desktop/gnome/interface/icon_theme"], stdout=subprocess.PIPE)
        return retcall.stdout.readline().strip('\n')
    
    def GetAvailableUsers(self, ):
        retcall = subprocess.Popen(["ck-history", "--frequent", "--seat=Seat1","--session-type="], stdout=subprocess.PIPE)
        UserList = []
        for user in retcall.stdout.readlines():
            UserList.append(user.split()[0])
        return UserList
