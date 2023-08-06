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

# eventHandlers.py


from enpraxis.educommons.interfaces import ICourse, IDivision
from Products.CMFDefault.SyndicationTool import SyndicationTool
from Products.CMFDefault.SyndicationInfo import SyndicationInformation
from collective.contentlicensing.utilities.interfaces import IContentLicensingUtility
from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility
from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IContainerModifiedEvent

from zope.schema.interfaces import IVocabularyFactory
from zope.formlib.form import action
from utilities.interfaces import IECUtility
from zope.component import getUtility, queryUtility
import transaction
from xml.dom import minidom
import mimetypes
import re
from App.config import getConfiguration
import os


RE_BODY = re.compile('<body[^>]*?>(.*)</body>', re.DOTALL )

def syndicateFolderishObject(object, event):
    """ Enable RSS feed upon FolderishObject creation. """
    if not hasattr(object.aq_explicit, 'syndication_information'):
        syInfo = SyndicationInformation()
        object._setObject('syndication_information', syInfo)
        portal = object.portal_url.getPortalObject()
        portal_syn = portal.portal_syndication
        syInfo = object._getOb('syndication_information')
        syInfo.syUpdatePeriod = portal_syn.syUpdatePeriod
        syInfo.syUpdateFrequency = portal_syn.syUpdateFrequency
        syInfo.syUpdateBase = portal_syn.syUpdateBase
        syInfo.max_items = portal_syn.max_items
        syInfo.description = "Channel Description"

def addObjPosition(object, event):
    appendObjPosition(object)

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
                    
    

def updateZipDownload(object, event):
    """ Check for factors related to editing and adding objects """
    pw = event.object.portal_workflow

    if pw.getInfoFor(event.object,'review_state') == 'Published':
        validateContext(object, event)

    

def ZipFileMaker(event):
    """ Handler for creating zip download for objects that are moving through workflow changes """

    if event.bulkChange and event.target in ['manager_rework','retract']:
        validateContext(event.object,event)        
    elif event.initial_state == 'Published' or event.target == 'publish':
        validateContext(event.object,event)
    else:
        pass 

def deleteObjectHandler(event):
    """ Handlet the delete object event """
    if event.bulkChange == True:
        if event.contains_published:
            validateContext(event.object, event)
    else:
        validateContext(event.object, event)


def validateContext(object, event):
    """ create the Zipfile after some final checks """

    parent = getUtility(IECUtility).FindECParent(object)
    file_id = parent.id + '.zip'
    pw = event.object.portal_workflow
    
    if parent.portal_type == 'Course':
        if pw.getInfoFor(parent,'review_state') == 'Published':
            if not event.object.isTemporary():
                if event.object.id != file_id:
                    if not IContainerModifiedEvent.providedBy(event):
                        ZipFileCreator(parent,event).createZipFile()




## Deprecated for 3.1.0, as auto generated Course packages have been disabled
## Replaced by Package Course functionality :: browser/packagecourseview.py
class ZipFileCreator:

    def __init__(self, object, event):
        self.obj = object
        self.event = event

    def createZipFile(self):
        """ Create a zip file for when the file is modified. """

        course = self.obj
        file_id = course.id + '.zip'

        pm = course.portal_membership
        user_id = pm.getAuthenticatedMember().id
        roles = pm.getAuthenticatedMember().getRoles()
        if 'Publisher' in roles:
            roles += ['Administrator']
            course.manage_setLocalRoles(user_id, roles)
            course.reindexObjectSecurity()

        data = self.getZipFileData(course=course)

        if not data:
            return

        if not hasattr(course,file_id):
                    
            course.invokeFactory("File",file_id)
            fileobj = getattr(course,file_id)
            fileobj.content_status_modify(workflow_action='submit')
            fileobj.content_status_modify(workflow_action='release')
            fileobj.content_status_modify(workflow_action='publish')
            fileobj.setTitle("Download This Course")

        else:
            fileobj = getattr(course,file_id)            
            fileobj.setTitle("Download This Course")

        
        fileobj.setExcludeFromNav(False)
        fileobj.setFile(data)
        appendObjPosition(fileobj)

        course.portal_catalog.reindexObject(fileobj)
        user_ids = []
        user_ids += [user_id]
        course.manage_delLocalRoles(userids=user_ids)
        course.reindexObjectSecurity()

    def getZipFileData(self, course, obj_paths=[], filename=None):
        """
        Return the content for a zip file
        """
        objects_list = getUtility(IZipFileTransportUtility)._createObjectList(course, obj_paths, state=['Published'])
        objects_list.insert(0,course)
        context_path = str( course.virtual_url_path() )

        # Do not include the zip file for the course
        mod_objects_list = [object for object in objects_list if object.virtual_url_path().replace(course.virtual_url_path(),'') != '/' + course.id + '.zip']
        
        if mod_objects_list:
            content = getUtility(IZipFileTransportUtility)._getAllObjectsData(mod_objects_list, context_path)
            return content
        else:
            return None

