A FTP service around Zope - allows resumable large file uploads into Zope.

It attempts to authentication using the same username/password against a Zope 
server. When the file is completely uploaded from the user, it then FTPs the 
file into a Plone-style folder hierarchy using the inbuilt Zope FTP server,
then deletes the temporary file.

You need to copy plumiftp.cfg to /etc, and configure it to your needs. This
location is not currently configurable; if you want to change it you will
need to edit zope_ftpd.py and change the string /etc/plumiftp.cfg manually

After installing, you can copy plumiftp.initscript to your /etc/init.d 
directory and (rename to plumiftp). Make sure the PATH and DAEMON variables
will be able to find the plumiftp script. You will either have to symlink
to the script from the relevant runlevels (/etc/rcX.d), or on Debian-style
systems you can run 'update-rc.d plumiftp defaults'

How to use Plumi FTP Access:
So, you have a large video that you _have not_ yet tried to
upload, because you know your internet connection is dodgy.
* Open an FTP client (e.g. filezilla, cyberduck, fireftp plugin)
* Connect your ftp client to ftp://your.server.name
* Log in as the user you use for the plone site on your server - if you do
not have a login you will need to create one via the normal process first
* Upload your file.
* If your connection was interrupted, try connecting, and upload
again. The ftp client should ask you if you want to resume the upload:
choose 'yes'
* When the upload is complete, go to 
http://your.plone.site/Members/<username>/videos/folder_content
* Click on your newly uploaded video, then click 'edit' to add the relevant 
meta-data


Requires Python 2.5+

--

Andy Nicholson
Victor Rajeswki
