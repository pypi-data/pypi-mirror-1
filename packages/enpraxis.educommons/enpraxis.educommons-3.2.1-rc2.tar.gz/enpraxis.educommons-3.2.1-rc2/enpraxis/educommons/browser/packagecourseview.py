##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved. 
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
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

from zope.publisher.browser import BrowserView
from Products.CMFPlone import PloneMessageFactory as _
from zope.component import getUtility, queryUtility
from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility
from zope.annotation.interfaces import IAnnotations
from enpraxis.educommons.utilities.interfaces import IECUtility
from Products.CMFCore.utils import getToolByName
from collective.imstransport.utilities.interfaces import IIMSTransportUtility


    
class PackageCourseView(BrowserView):
    """View to package a published course """

    def __call__(self):
        self.createIMSFile()
        message = _('Course has been packaged')
        url = '%s/folder_contents' % self.context.absolute_url()
        self.context.plone_utils.addPortalMessage(message)
        self.request.response.redirect(url)


    def createIMSFile(self):
        """ Package a Published Course. """

        course = self.context
        file_id = course.id + '.zip'

        pm = course.portal_membership
        user_id = pm.getAuthenticatedMember().id
        roles = pm.getAuthenticatedMember().getRoles()
        if 'Publisher' in roles:
            roles += ['Administrator']
            course.manage_setLocalRoles(user_id, roles)
            course.reindexObjectSecurity()

        #this needs to fire off IMS packaging instead of zip
        ims_util = getUtility(IIMSTransportUtility)
        data, course = ims_util.exportPackage(course, file_id, packagetype='IMS Common Cartridge')

        if not hasattr(course,file_id):
            course.invokeFactory("FSSFile",id=file_id, title="Download this Course")
            fileobj = getattr(course,file_id)
            wftool = getToolByName(fileobj, 'portal_workflow')
            wftool.doActionFor(fileobj, 'submit')
            wftool.doActionFor(fileobj, 'release')
            wftool.doActionFor(fileobj, 'publish')        
            fileobj.setTitle("Download This Course")
        else:
            fileobj = getattr(course,file_id)            
            fileobj.setTitle("Download This Course")
        
        fileobj.setExcludeFromNav(True)
        fileobj.setFile(data)
        appendObjPosition(fileobj)

        course.portal_catalog.reindexObject(fileobj)
        user_ids = []
        user_ids += [user_id]
        course.manage_delLocalRoles(userids=user_ids)
        course.reindexObjectSecurity()




def appendObjPosition(object):
    if not object.isTemporary():
        ecutil = queryUtility(IECUtility)
        if ecutil:
            parent = ecutil.FindECParent(object)
            if parent.Type() == 'Course':
                path = {'path':{'query':'/'.join(parent.getPhysicalPath())+'/'},}
                brains = object.portal_catalog.searchResults(path)
                if brains:
                    pos = [0,]
                    for brain in brains:
                        obj = brain.getObject()
                        annotations = IAnnotations(obj)
                        if annotations.has_key('eduCommons.objPositionInCourse'):
                            pos += [annotations['eduCommons.objPositionInCourse'],]
                    maxpos = max(pos)
                    if maxpos > 0:
                        maxpos += 1
                    else:
                        maxpos = 1
                else:
                    maxpos = 1
                
                annotations = IAnnotations(object)
                annotations['eduCommons.objPositionInCourse'] = maxpos

                zipobj = getattr(parent, parent.id + '.zip', None)
                if zipobj:
                    IAnnotations(zipobj)['eduCommons.objPositionInCourse'] = maxpos + 1
                    zipobj.reindexObject()
