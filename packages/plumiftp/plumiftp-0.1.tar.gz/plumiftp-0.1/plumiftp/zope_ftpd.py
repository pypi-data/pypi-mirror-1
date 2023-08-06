"""
A FTP service around Zope - allows resumable large file uploads into Zope.

It attempts to authentication using the same username/password against a Zope server. When the file is completely uploaded from the 
user, it then FTPs the file into a Plone-style folder hierarchy using the inbuilt Zope FTP server.

"""

"""
    Plumi FTP wrapper 
    Copyright (C) 2009 Andy Nicholson, Victor Rajewski, EngageMedia Collective Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    see LICENSE.txt in the source distribution for the GNU GPL v3 details. 
"""

import os
import ftplib
import threading

from pyftpdlib import ftpserver

from config import ZopeFTPServerAddr, ZopeFTPServerPort, ZopePathString, TmpDir, RealFTPMsgLogin, RealFTPMsgQuit, RealFTPServerAddress, RealFTPServerPort

class ZopeAuthorizer(ftpserver.DummyAuthorizer):

    def validate_authentication(self, username, password):

	#
	# proxied Zope FTP server authentication.
	#
        zopeftp=ftplib.FTP()
        try: 
	    #Zope FTP lets you in with an incorrect password.
	    # however, if you get it wrong, you can't see any files or write anything.
	    # hence --> we need a test here to do something remotely and really check if we
	    # got the password wrong. Trying to 'cd' into our Members area is good enough to raise an 'not authenicated' error.

            zopeftp.connect(ZopeFTPServerAddr, ZopeFTPServerPort)
            zopeftp.login(username, password)
    	    #login to our plone site's members area ..
            zopeftp.cwd(ZopePathString%username)

        except ftplib.all_errors, detail:
            ftpserver.log("Error authenticating to Zope FTP server %s:%s \
                           with username %s : %s" % (ZopeFTPServerAddr, 
                           ZopeFTPServerPort, username, detail))
            return False
        finally:
            zopeftp.close()


	# Local server setup.
	#
        #create user path if not already present. If present and not a dir
        #then delete it and create a dir (shouldn't happen, but...)
        userpath = TmpDir + "/" + username
        try:
            if os.path.exists(userpath):
                if not os.path.isdir(userpath):
                    os.remove(userpath) 
                    os.makedirs(userpath)
            else:
                os.makedirs(userpath)
        except OSError, detail:
            #if there is a problem creating the folders then the ftp server
            #will return 'Authentication failed'
            ftpserver.log("Error creating temporary user directory %s: %s" 
                          % (userpath, detail))
            return False

	# 
	# successfully logged in for our purposes.
	#
	ftpserver.log('authenticated successfully with Plumi FTP')
        return True

    def has_perm(self, username, perm, path=None):
        return True

    def get_perms(self, username):
        return 'elradfmw'

    def get_home_dir(self, username):
        return TmpDir + "/" + username

    def get_msg_login(self, username):
        return RealFTPMsgLogin

    def get_msg_quit(self, username):
        return RealFTPMsgQuit

class ZopeHandler(ftpserver.FTPHandler):
    def on_file_received(self,file):
        ftpserver.log("ZopeHandler: we got %s, from user %s, with password %s "
                      % (file, self.username, self.password))
        def ZopeUpload():
            #ftp it into Zope itself.
            try:
                zopeftp=ftplib.FTP()
                zopeftp.connect(ZopeFTPServerAddr, ZopeFTPServerPort)
                zopeftp.set_pasv(True)
                zopeftp.login(self.username,self.password)
                #login to our plone site's members area ..
                zopeftp.cwd(ZopePathString%self.username)
                #upload the file
                f = open(file,'rb')                # open file to send
                zopeftp.storbinary('STOR %s' % os.path.basename(file), f) # Send file
                ftpserver.log("Successfully uploaded %s to Zope FTP server"
                             % (file))
            except ftplib.all_errors, detail:
                ftpserver.log("Error sending file %s to Zope FTP server %s:%s \
                               with username %s : %s"
                              % (file, ZopeFTPServerAddr, ZopeFTPServerPort, 
                                 self.username, detail))
            except IOError, detail:
                ftpserver.log("Error opening local file %s for sending to \
                               Zope FTP : %s" % (file, detail))
            finally:
                zopeftp.close()
                f.close()
                try:
                    os.remove(file)
                except OSError, detail:
                    ftpserver.log("Error deleting temp file %s : %s" 
                                  % (file, detail))
                self.sleeping = False

        self.sleeping = True
        threading.Thread(target=ZopeUpload).start()

def plumiftp_wrapper():
    authorizer = ZopeAuthorizer()
    ftp_handler = ZopeHandler
    ftp_handler.authorizer = authorizer
    address = (RealFTPServerAddress, RealFTPServerPort)
    ftpd = ftpserver.FTPServer(address, ftp_handler)
    ftpd.serve_forever()
