##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved.
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation; either version 2 of the License, or            
#    (at your option) any later version.                                          
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from collective.imstransport.utilities.objcreator import ObjectCreator
from collective.contentlicensing.utilities.interfaces import IContentLicensingUtility
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations

class eduObjectCreator(ObjectCreator):
    """ Create objects from IMS manifest. """

    def applyMetadata(self, obj, data):
        """ Overridden to handle situations with IAnnotations and licenses """

        for key in data.keys():
            if key == 'accessible':
                IAnnotations(obj)['eduCommons.accessible'] = data[key]
            elif key == 'clearedCopyright':
                IAnnotations(obj)['eduCommons.clearcopyright'] = data[key]
            elif key == 'license':
                cltool = getUtility(IContentLicensingUtility)
                cltool.setRightsLicense(obj, data['license'])
            elif key not in  ['file', 'id', 'type']:
                field = obj.getField(key)
                if field:
                    mutator = field.getMutator(obj)
                    if mutator:
                        mutator(data[key])
