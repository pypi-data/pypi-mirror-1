#directory to store uploads until they are sent to zope
TmpDir="/tmp/plumiFTP"

#replace this with the address (name or IP) and port of your zope FTP server
ZopeFTPServerAddr="your.zope.server.address"
ZopeFTPServerPort=8021
#this is where the uploaded files end up. Replace plumi-id with the ID of your
#Plumi or Plone site. %s will be replaced by the username.
ZopePathString="/plumi-id/Members/%s/videos" 

#Address and port for the real ftp server to listen on. By default will only
#listen to localhost, so if you want this to be useful, replace with an 
#external facing address, or set to an empty string to listen on all interfaces
RealFTPServerAddress="127.0.0.1"
RealFTPServerPort=21

#Hello and Goodbye messages. 
RealFTPMsgLogin="Welcome to Plumi FTP"
RealFTPMsgQuit="Thanks for using Plumi FTP!"
