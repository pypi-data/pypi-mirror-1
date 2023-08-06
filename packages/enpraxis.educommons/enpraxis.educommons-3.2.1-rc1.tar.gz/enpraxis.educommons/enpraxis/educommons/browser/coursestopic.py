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

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from enpraxis.educommons.utilities.interfaces import IECUtility
from enpraxis.educommons.interfaces import IOpenOCWSite
from zope.component import getUtility

class CoursesView(BrowserView):
    """ A course listing view """

class DivisionCourseListView(BrowserView):
    """ A course listing view for a division """

    __call__ = ViewPageTemplateFile('divisioncourses.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.ecutil = getUtility(IECUtility)

    def getCourses(self):
        path = {'query':'/'.join(self.context.getPhysicalPath()) + '/'}
        results = self.context.portal_catalog.searchResults(path=path, portal_type='Course')
        results = list(results)
        results.sort(lambda x, y : cmp(self.ecutil.getFullCourseTitle(x), self.ecutil.getFullCourseTitle(y)))
        return results

    def getFullCourseTitle(self, brain):
        """ Returns the title with term and ID information  """
        full_title = self.ecutil.getFullCourseTitle(brain)
        return full_title

        
class ProfCourseListView(BrowserView):
    """ A course listing view for a professor """

    __call__ = ViewPageTemplateFile('profslisting.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.ecutil = getUtility(IECUtility)
        self.current_instructor = ''

    def getCoursesByInstructor(self, brains):
        """ Aggregates Courses by Instructor Name  """
        iname = ''
        courselist = []
        tlist = None

        for x in brains:
            if x.portal_type == 'Course':
                if iname != x.getInstructorName:
                    if tlist:
                        courselist.append((iname, tlist))
                    tlist = [x]
                    iname = x.getInstructorName 
                else:
                    if tlist:
                        tlist.append(x)
                        #Sort by full Course title
                        tlist = list(tlist)
                        tlist.sort(lambda x, y : cmp(self.ecutil.getFullCourseTitle(x),self.ecutil.getFullCourseTitle(y)))
                    else:
                        tlist = [x]
            
        if tlist:
            courselist.append((iname, tlist))

        return courselist

    def getProfName(self, name):
        """ Returns the professor's name, or default string if none exists """
        if name == '':
            return 'No Professor Listed'
        return name

    def getFullCourseTitle(self, brain):
        """ Returns the title with term and ID information  """
        full_title = self.ecutil.getFullCourseTitle(brain)
        return full_title

    def getOddEvenClass(self, oddrow=None):
        """ assigns a css class based on odd even in the tal repeat  """
        cssclass = 'course-listing odd'
        if oddrow:
            cssclass = 'course-listing even'
        return cssclass
        

class DivisionPageView(BrowserView):
    """ A default divison page view """

    __call__ = ViewPageTemplateFile('templates/division_view.pt')

    def isOpenOCW(self):
        return IOpenOCWSite.providedBy(self.context.portal_url.getPortalObject())
        

class CoursePageView(BrowserView):
    """ A default course page view """

    __call__ = ViewPageTemplateFile('templates/course_view.pt')
