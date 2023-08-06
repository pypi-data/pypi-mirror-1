Installation
============

If you have sucessfully configured and installed the Red5 server
(http://osflash.org/red5), you have to install the protectedVOD red5
application.

   - bash> cd /<path to red5>/webapps
   - bash> mkdir protectedVOD
   - bash> cd protectedVOD
   - bash> jar xvf protectedVOD_0.1-java6.war
   - The secret in WEB-INF/red5-web.properties should match the value in plone's portal_properties/red5_protectedvod_properties
   - bash> cd streams
   - bash> ln -s /<path to plone's fss>/ .
   - restart Red5

