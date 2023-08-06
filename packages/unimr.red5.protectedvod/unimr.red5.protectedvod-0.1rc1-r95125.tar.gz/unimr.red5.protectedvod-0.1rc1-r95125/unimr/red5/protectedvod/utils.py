##   unimr.red5.protectedVod is copyright
##   Andreas Gabriel <gabriel@hrz.uni-marburg.de>

##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2 of the License, or
##   (at your option) any later version.

##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
##   GNU General Public License for more details.

##   You should have received a copy of the GNU General Public License
##   along with this program; if not, write to the Free Software
##   Foundation, Inc., 59 Temple Place, Suite 330, Boston,
##   MA 02111-1307 USA.



from zope.interface import implements
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.PythonScripts.standard import url_quote_plus
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime 

from plone.memoize.view import memoize

from interfaces import IRed5ProtectedVodTool

import logging
import hmac


logger = logging.getLogger('unimr.red5.protectedvod')

            

class Red5ProtectedVodTool(BrowserView):
    """A view that implements a hmac algorithm for url signatures
       in interaction with a red5 streaming server
    """
    implements(IRed5ProtectedVodTool)


    def netConnectionUrl(self,fieldname='file'):
        """ returns the netConnectionUrl including path, signature and expire date"""

        data = self._signature_data(fieldname=fieldname)

        return "%(server_url)s/%(path)s/%(signature)s/%(expires)s" % data


    def clip(self,fieldname='file'):
        """ return clip's name """
        
        data = self._signature_data(fieldname=fieldname)
        
        return "%(filename)s" % data


    @memoize
    def _signature_data(self,fieldname='file'):

        context = aq_inner(self.context)
        request = self.request
        
        properties_tool = getToolByName(context, 'portal_properties')
        hmac_properties = getattr(properties_tool, 'red5_protectedvod_properties', None)

        red5_server_url = hmac_properties.getProperty('red5_server_url')
        red5_server_url = red5_server_url.rstrip('/')

        secret_phrase = hmac_properties.getProperty('secret')

        try:
            ttl = int(hmac_properties.getProperty('ttl'))
        except ValueError:
            ttl = 60


        clientip=request.get('HTTP_X_FORWARDED_FOR',None)
        if not clientip:
            clientip=request.get('REMOTE_ADDR',None)

        expires = "%08x" % (DateTime().timeTime() + ttl)       

        (path, filename) = self._fss_info(fieldname)

        sign_path = "/%s/" % (path,)
        
        signature = hmac_hexdigest(secret_phrase,[sign_path,filename,clientip,expires])

        data={
            "server_url":  red5_server_url,
            "sign_path" : sign_path,
            "path" : path,
            "filename": filename,
            "expires" : expires,
            "clientip" : clientip,
            "signature" : url_quote_plus(signature)
            }
        
        logger.debug(data)
        return data
    
    def _fss_info(self,fieldname='file'):
        
        context = aq_inner(self.context)
        
        field = context.getField(fieldname)
        storage = field.storage
        
        try:
            info = storage.getFSSInfo(fieldname, context)  
            strategy = storage.getStorageStrategy(fieldname, context)
            props = storage.getStorageStrategyProperties(fieldname, context, info)
        except AttributeError:
            logger.error('cannot retrieve fss properties. fss installed?')
            return


        valueDirectoryPath=strategy.getValueDirectoryPath(**props)
        valueFilename=strategy.getValueFilename(**props)

        length = len(strategy.storage_path.split('/'))
        
        path = '/'.join(valueDirectoryPath.split('/')[length-1:]).strip('/')
        
        return (path, valueFilename)



def hmac_hexdigest(secret,update_list):
    """ returns a hex encoded digest of signature """
    mac = hmac.new(secret)
    for s in update_list:
        mac.update(s)

    return mac.hexdigest()








