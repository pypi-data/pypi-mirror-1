==================================
 tasktracker opencore integration
==================================

URI convenience api
===================

    >>> from opencore.tasktracker import uri as tt_uri

#@@ this should be cleaned up and return none

    >>> tt_uri.get() 
    u'http://localhost:5050'

featurelet install
==================

    >>> from opencore.tasktracker.featurelet import TaskTrackerFeaturelet
    >>> ttf = TaskTrackerFeaturelet()

The mock http should be hooked up::

    >>> ttf.http
    <HTTPMock ... httplib2.Http>

Calling request(uri) on the mock http will return a (response, content)
tuple like httplib2.Http.request()::
    >>> response, content = ttf.http.request('http://nohost')
    Called ...

The response is set up to return status code 200::
    >>> response.status
    200
    >>> content
    'Mock request succeeded!'

We will simulate 'deliverPackage' and 'removePackage', the http calls
to tasktracker::

    >>> project = self.app.plone.projects.p1
    >>> header = {"X-Tasktracker-Initialize":"True"}
    >>> ttf._makeHttpReqAsUser(ttf.init_uri, obj=project, headers=header)
    Called httplib2.Http.request(
        u'http://localhost:5050/project/initialize/',
        headers={'X-Openplans-Project': 'p1', 'Cookie': '__ac=...', 'X-Tasktracker-Initialize': 'True'},
        method='POST')
    (<...MockResponse object at ...>, 'Mock request succeeded!')
    >>> ttf._makeHttpReqAsUser(ttf.uninit_uri, obj=project)
    Called httplib2.Http.request(
        u'http://localhost:5050/project/uninitialize/',
        headers={'X-Openplans-Project': 'p1', 'Cookie': '__ac=...'},
        method='POST')
    (<...MockResponse object at ...>, 'Mock request succeeded!')
