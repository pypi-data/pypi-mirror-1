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

from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Products.contentmigration.basemigrator.walker import CatalogWalker 
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.component import getUtility, getMultiAdapter
from zope.interface import directlyProvidedBy, directlyProvides
from Products.CMFPlone.PloneTool import transaction
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping

# base class to migrate objects and retain their license annotations
class eduCommonsFoldersMigrator(CMFFolderMigrator):
    """Persist annotations to new object"""

    def migrate_annotations(self):
        """Persist annotations"""
        if hasattr(self.old, '__annotations__'):
            annotations = self.old.__annotations__
            self.new.__annotations__ = annotations
            
    def migrate_clearcopyright(self):
        """Migrate clear copyright status to annotation """
        if hasattr(self.old, 'clearedCopyright'):
            copyright_status = self.old.getClearedCopyright()
            """ Manually append field to default content type  """
            self.new.__annotations__['eduCommons.clearcopyright'] = copyright_status

    def migrate_current_workflow(self):
        """Annotate the current workflow state"""
        wft = self.old.portal_url.portal_workflow
        cur_state = wft.getInfoFor(self.old, 'review_state')
        self.new.__annotations__['review_state'] = cur_state


class CourseMigrator(eduCommonsFoldersMigrator):
    """Base class to migrate to Folder """
    
    def migrate_courseproperties(self):
        """Place course specific fields in an annotation, to be used in 3.1.1 to 3.2.1 migration """
        if hasattr(self.old, 'term'):
            self.new.__annotations__['course.term'] = self.old.term
        if hasattr(self.old, 'courseId'):
            self.new.__annotations__['course.courseid'] = self.old.courseId
        if hasattr(self.old, 'structure'):
            self.new.__annotations__['course.structure'] = self.old.structure            
        if hasattr(self.old, 'level'):
            self.new.__annotations__['course.level'] = self.old.level
        if hasattr(self.old, 'instructorName'):
            self.new.__annotations__['course.instructorname'] = self.old.instructorName
        if hasattr(self.old, 'instructorAsCreator'):
            self.new.__annotations__['course.instructor_principal'] = self.old.instructorAsCreator
        if hasattr(self.old, 'instructorEmail'):
            self.new.__annotations__['course.instructoremail'] = self.old.instructorEmail
        if hasattr(self.old, 'displayInstEmail'):
            self.new.__annotations__['course.displayInstructorEmail'] = self.old.displayInstEmail
        if hasattr(self.old, 'crosslisting'):
            self.new.__annotations__['course.crosslisting'] = self.old.crosslisting            
        text = self.old.getText()
        self.new.__annotations__['course.text'] = text
        
    def migrate_portlets(self):
        """ Remove the portlets associated with the course """
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.new)
        right = getMultiAdapter((self.new, rightColumn), IPortletAssignmentMapping, context=self.new)
        del right['OER Recommender']
        del right['Course Summary']
        del right['Reuse Course']        

    walkerClass = CatalogWalker
    src_meta_type = 'Course'
    src_portal_type = 'Course'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'

class DivisionMigrator(eduCommonsFoldersMigrator):
    """Base class to migrate to Folder """

    def migrate_deptproperties(self):
        """Place course specific fields in an annotation, to be used in 3.1.1 to 3.2.1 migration """
        text = self.old.getText()
        self.new.__annotations__['dept.text'] = text


    walkerClass = CatalogWalker
    src_meta_type = 'Division'
    src_portal_type = 'Division'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'

def pre_migrate_3_1_1_to_3_2_1(self):
    """Run the migration"""
     
    out = StringIO()
    print >> out, "Starting migration"
         
    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()

    #create migrateable_properties to migrate old site props
    portal.portal_properties.addPropertySheet('migrateable_properties', 'Old Site Properties')
    m_props = portal.portal_properties.migrateable_properties
   
    m_props.manage_addProperty(id='site_title', type='string', value=portal.title)
    m_props.manage_addProperty(id='description', type='string', value=portal.description)
    m_props.manage_addProperty(id='email_from_address', type='string', value=portal.email_from_address)
    m_props.manage_addProperty(id='email_from_name', type='string', value=portal.email_from_name)

    migrators = ( DivisionMigrator, CourseMigrator)

    for migrator in migrators:
        walker = migrator.walkerClass(portal, migrator)
        walker.go(out=out)
        transaction.commit()
        print >> out, walker.getOutput()

    #Refresh catalog indices
    self.portal_catalog.reindexIndex(self.portal_catalog.indexes(),None)

    print >> out, "Migration finished"
    return out.getvalue()


