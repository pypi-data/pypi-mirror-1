from DateTime import DateTime as zopedatetime
from zExceptions import Redirect 
import re

from Products.AdvancedQuery import Eq, RankByQueries_Sum
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch

from topp.utils.pretty_date import prettyDate
from opencore.nui.base import BaseView, static_txt
from opencore import redirect

num_regex = re.compile('((the|a|an)\s+)?[0-9]+')

def first_letter_match(title, letter):
    if letter == 'num':
        return num_regex.match(title)
    else:
        return title.startswith(letter) \
               or title.startswith('the ' + letter) \
               or title.startswith('a ' + letter) \
               or title.startswith('an ' + letter)


class SearchView(BaseView):
    match = staticmethod(first_letter_match)

    def project_url(self, project_brain):
        return '%s/projects/%s' % (self.context.absolute_url(),
                                   project_brain.getId)

    def _get_batch(self, brains, start=0):
        return Batch(brains,
                     size=10,
                     start=start,
                     end=0,
                     orphan=0,
                     overlap=0,
                     pagerange=6,
                     quantumleap=0,
                     b_start_str='b_start')

    def add_class_to_img(self, imgdata, clss):
        tag = str(imgdata)
        return tag.replace('<img', '<img class="%s"' % clss)

class ProjectsSearchView(SearchView):

    active_states = ['public', 'private']

    def __call__(self):
        search_for = self.request.get('search_for', None)
        letter_search = self.request.get('letter_search', None)
        start = self.request.get('b_start', 0)
        sort_by = self.request.get('sort_by', None)
        self.search_results = None
        self.search_query = None

        # this resets pagination when the sort order is changed
        if self.request.get('REQUEST_METHOD', None) == 'POST':
            start = 0
            self.request.set('b_start', 0)
            
        if letter_search:
            self.search_results = self._get_batch(self.search_for_project_by_letter(letter_search, sort_by), start)
            self.search_query = 'for projects starting with &ldquo;%s&rdquo;' % letter_search
        elif search_for:
            self.search_results = self._get_batch(self.search_for_project(search_for, sort_by), start)
            self.search_query = 'for &ldquo;%s&rdquo;' % search_for
        else:
            self.search_results = self._get_batch(self.search_for_project_by_letter('all', sort_by), start)
            self.search_query = 'for all projects'
            
        return self.index()
        
    def search_for_project_by_letter(self, letter, sort_by=None):
        letter = letter.lower()

        if letter == 'num':
            search_for = '1* OR 2* OR 3* OR 4* OR 5* OR 6* OR 7* OR 8* OR 9* OR 0*'
            query = dict(portal_type="OpenProject", Title=search_for)
        elif letter == 'all':
            query = dict(portal_type="OpenProject")
        else:
            search_for = letter + '*'
            query = dict(portal_type="OpenProject", Title=search_for)



        if sort_by != 'relevancy':
            query['sort_on'] = sort_by

        self.apply_context_restrictions(query)

        project_brains = self.catalog(**query)

        if letter == 'all':
            return project_brains

        project_brains = [brain for brain in project_brains \
                          if self.match(brain.Title.lower(), letter)]

        return project_brains

    def search_for_project(self, project, sort_by=None):
        proj_query = project.lower().strip()

        if proj_query == '*':
            return []
        if not proj_query.endswith('*'):
            proj_query = proj_query + '*'

        if not sort_by or sort_by == 'relevancy':
            rs = RankByQueries_Sum((Eq('Title', proj_query),32),
                                   (Eq('getFull_name', proj_query),16)),
        else:
            # we can't sort by title
            if sort_by == 'Title':
                sort_by = 'sortable_title'
            rs = ((sort_by, 'desc'),)

        query = Eq('portal_type', 'OpenProject') & Eq('SearchableText', proj_query)

        query = self.adv_context_restrictions_applied(query)
        
        project_brains = self.catalog.evalAdvancedQuery(query, rs)
        return project_brains
    
    def recently_updated_projects(self, sort_limit=10):
        query = dict(portal_type='OpenProject',
                     sort_on='modified',
                     sort_order='descending',
                     sort_limit=sort_limit,
                     )

        self.apply_context_restrictions(query)

        project_brains = self.catalog(**query) 
        return project_brains

    def n_project_members(self, proj_brain):
        proj_id = proj_brain.getId
        tmtool = self.get_tool('portal_teams')
        team_path = '/'.join(tmtool.getPhysicalPath())
        team_path = '%s/%s' % (team_path, proj_id)
        brains = self.catalog(portal_type='OpenMembership',
                              path=team_path,
                              review_state=self.active_states,
                              )
        return len(brains)

    def apply_context_restrictions(self, query):
        """
        inserts additional query constraints into the
        query dict given based on context
        """
        pass

    def adv_context_restrictions_applied(self, adv_query):
        """
        returns a new advanced query based on the
        query given with additional constraints based
        on context
        """
        return adv_query


class SubProjectsSearchView(ProjectsSearchView):

    def subproject_paths(self):
        info = redirect.get_info(self.context)
        if info:
            return list(info.values())
        else:
            return []

    def all_subprojects(self):
        query = dict(portal_type="OpenProject",
                     sort_on='sortable_title')

        self.apply_context_restrictions(query)

        project_brains = self.catalog(**query)
        return project_brains
        
    def apply_context_restrictions(self, query):
        query['path'] = self.subproject_paths()

    def adv_context_restrictions_applied(self, query):
        return query & In('path', self.subproject_paths())


def searchForPerson(mcat, search_for, sort_by=None):
    """
    This is a function, not a method, so it can be called from
    assorted view classes.
    """
    person_query = search_for.lower().strip()

    if person_query == '*':
        return []

    if not person_query.endswith('*'):
        person_query = person_query + '*'

    if not sort_by or sort_by == 'relevancy':
        rs = (RankByQueries_Sum((Eq('Title', person_query),32),
                                (Eq('getId', person_query),16)),)
    else:
        rs = ((sort_by, 'desc'),)

    people_brains = mcat.evalAdvancedQuery(
        Eq('RosterSearchableText', person_query),
        rs,
        )
    return people_brains
    

class PeopleSearchView(SearchView):

    def __init__(self, context, request):
        SearchView.__init__(self, context, request)

    def __call__(self):
        search_for = self.request.get('search_for', None)
        letter_search = self.request.get('letter_search', None)
        start = self.request.get('b_start', 0)
        sort_by = self.request.get('sort_by', None)
        self.search_results = None
        self.search_query = None

        # this resets pagination when the sort order is changed
        if self.request.get('REQUEST_METHOD', None) == 'POST':
            start = 0
            self.request.set('b_start', 0)
            
        if letter_search:
            self.search_results = self._get_batch(self.search_for_person_by_letter(letter_search, sort_by), start)
            self.search_query = 'for members starting with &ldquo;%s&rdquo;' % letter_search
        elif search_for:
            self.search_results = self._get_batch(self.search_for_person(search_for, sort_by), start)
            self.search_query = 'for &ldquo;%s&rdquo;' % search_for
        else:
            self.search_results = self._get_batch(self.search_for_person_by_letter('all', sort_by), start)
            self.search_query = 'for all members'
            
        return self.index()

    def search_for_person_by_letter(self, letter, sort_by=None):
        letter = letter.lower()

        if letter == 'num':
            search_for = '1* OR 2* OR 3* OR 4* OR 5* OR 6* OR 7* OR 8* OR 9* OR 0*'
            query = dict(RosterSearchableText=search_for)
        elif letter == 'all':
            query = {}
        else:
            search_for = letter + '*'
            query = dict(RosterSearchableText=search_for)

        if sort_by != 'relevancy':
            query['sort_on'] = sort_by

        people_brains = self.membranetool(**query)

        if letter == 'all':
            return people_brains
        elif letter == 'num':
            people_brains = [brain for brain in people_brains
                             if num_regex.match(brain.getId.lower())]
        else:
            people_brains = [brain for brain in people_brains
                             if brain.getId.lower().startswith(letter)]
        return people_brains

    def search_for_person(self, person, sort_by=None):
        return searchForPerson(self.membranetool, person, sort_by)

    anonymous_txt = static_txt('main_people_anonymous.txt')

class HomeView(SearchView):
    """zpublisher"""
    def __init__(self, context, request):
        # redirect asap
        go_here = request.get('go_here', None)
        if go_here:
            raise Redirect, go_here        
        SearchView.__init__(self, context, request)

        self.projects_search = ProjectsSearchView(context, request)

    intro = static_txt('main_home_intro.txt')

    def recently_updated_projects(self):
        return self.projects_search.recently_updated_projects(sort_limit=5)

    def n_project_members(self, proj_brain):
        return self.projects_search.n_project_members(proj_brain)

    def recently_created_projects(self):
        query = dict(portal_type='OpenProject',
                     sort_on='created',
                     sort_order='descending',
                     sort_limit=5,
                     )

        project_brains = self.catalog(**query) 
        return project_brains

    def news(self):
        news_path = '/'.join(self.context.portal.getPhysicalPath()) + '/news'
        query = dict(portal_type='Document',
                     sort_on='created',
                     sort_order='descending',
                     sort_limit=4,
                     path=news_path
                     )
        brains = self.catalog(**query)
        return brains
    
    aboutus = static_txt('main_home_aboutus.txt')


class SitewideSearchView(SearchView):

    def __call__(self):
        letter_search = self.request.get('letter_search', None)
        search_for = self.request.get('search_for', None)
        start = self.request.get('b_start', 0)
        sort_by = self.request.get('sort_by', None)
        self.search_results = None
        self.search_query = None

        # this resets pagination when the sort order is changed
        if self.request.get('REQUEST_METHOD', None) == 'POST':
            start = 0
            self.request.set('b_start', 0)
            
        if letter_search:
            self.search_results = self._get_batch(self.search_by_letter(letter_search, sort_by), start)
            self.search_query = 'for content starting with &ldquo;%s&rdquo;' % letter_search
        elif search_for:
            self.search_results = self._get_batch(self.search(search_for, sort_by), start)
            self.search_query = 'for &ldquo;%s&rdquo;' % search_for
        else:
            self.search_results = self._get_batch(self.search_by_letter('all', sort_by), start)
            self.search_query = 'for all content'
            
        return self.index()
    

    def _sort_by_id(self, brains):
        return sorted(brains, key=lambda x: x.portal_type == 'OpenMember' \
                      and x.getId.lower() or x.Title.lower())
    

    def search_by_letter(self, letter, sort_by=None):
        letter = letter.lower()
        if letter == 'num':
            search_for = '1* OR 2* OR 3* OR 4* OR 5* OR 6* OR 7* OR 8* OR 9* OR 0*'
            query = (Eq('portal_type', 'OpenProject') & Eq('Title', search_for)) \
                    | (Eq('portal_type', 'Document') & Eq('Title', search_for)) \
                    | (Eq('portal_type', 'OpenMember') & Eq('Title', search_for))
        elif letter == 'all':
            query = Eq('portal_type', 'OpenProject') \
                    | Eq('portal_type', 'Document') \
                    | Eq('portal_type', 'OpenMember')
        else:
            search_for = letter + '*'
            query = (Eq('portal_type', 'OpenProject') & Eq('Title', search_for)) \
                    | (Eq('portal_type', 'Document') & Eq('Title', search_for)) \
                    | (Eq('portal_type', 'OpenMember') & Eq('Title', search_for))

        if not sort_by or sort_by == 'relevancy':
            rs = ()
        else:
            if sort_by == 'getId':
                rs = ()
            else:
                rs = ((sort_by, 'desc'),)

        brains = self.catalog.evalAdvancedQuery(query, rs)

        if sort_by == 'getId':
            brains = self._sort_by_id(brains)

        if letter == 'all':
            return brains
        
        out_brains = []
        
        for brain in brains:
            if brain.portal_type in ('OpenProject', 'Document') and \
                   self.match(brain.Title.lower(), letter):
                out_brains.append(brain)
            elif brain.portal_type == ('OpenMember') and \
                    brain.getId.lower().startswith(letter):
                out_brains.append(brain)
                
        return out_brains



    def search(self, search_for, sort_by=None):
        search_query = search_for.lower().strip()

        if search_query == '*':
            return []

        if not search_query.endswith('*'):
            search_query = search_query + '*'

        if not sort_by or sort_by == 'relevancy':
            rs = (RankByQueries_Sum((Eq('getId', search_query),32), (Eq('getFull_name', search_query),16)),)
        else:
            if sort_by == 'getId':
                rs = ()
            else:
                rs = ((sort_by, 'desc'),)

        query = (Eq('portal_type', 'OpenProject') \
                | Eq('portal_type', 'Document') \
                | Eq('portal_type', 'OpenMember')) \
                & Eq('SearchableText', search_query)
        brains = self.catalog.evalAdvancedQuery(query, rs)

        if sort_by == 'getId':
            brains = self._sort_by_id(brains)

        return brains
    

class NewsView(SearchView):

    def news_items(self):
        news_path = '/'.join(self.context.portal.getPhysicalPath()) + '/news'
        query = dict(portal_type='Document',
                     sort_on='created',
                     sort_order='descending',
                     sort_limit=20,
                     path=news_path
                     )
        brains = self.catalog(**query)
        return brains
        
    def can_add_news(self):
        return self.membertool.checkPermission('Manage Portal', self.context)

    def subpoena_free(self):
        delta = zopedatetime() - self.dob_datetime
        return int(delta)

    def _get_new_id(self):
        # if you don't like this
        # return zopedatetime().millis()
        # this is informative
        return zopedatetime().strftime('%Y%m%d%H%M%S')

    def add_new_news_item(self):
        new_id = self._get_new_id()
        self.context.invokeFactory('Document', id=new_id, title=new_id)
        item = getattr(self.context, new_id)
        edit_url = '%s/edit' % item.absolute_url()
        self.request.response.redirect(edit_url)

    sidebar = static_txt('main_news_sidebar.txt')

