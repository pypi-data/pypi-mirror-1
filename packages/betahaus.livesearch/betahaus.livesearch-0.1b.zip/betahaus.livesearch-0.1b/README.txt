Introduction
============


This is a replacement for the standard Plone livesearch. It acts and looks exactly the same as the standard one,
the only difference is that it is implemented using a browser template ad view instead of the nasty skins script that is shipped.

The reason for making this product is that you easier can change the layout of the livesearch.

All you need to do is to install and you will not notice any difference.

Installation
------------

buildout:
 - Add ``betahaus.livesearch`` entries to eggs and zcml in the appropriate buildout configuration file. (typcially buildout.cfg) 
 - Re-run buildout. (./bin/buildout)
 - Restart the instance
 - Install via portal_quickinstaller or Site Setup in plone

 