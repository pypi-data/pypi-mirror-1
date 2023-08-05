 wiki ui
=========

    >>> page_id = self.portal.projects.p1.getDefaultPage()
    >>> page = getattr(self.portal.projects.p1, page_id)

Registrations
=============

Test wiki page registrations::

    >>> page.restrictedTraverse('@@view')
    <...SimpleViewClass from ...wiki/wiki-view.pt object at ...>
    
    >>> page.restrictedTraverse('@@wiki_macros')
    <...SimpleViewClass ...wiki/wiki_macros.pt object at ...>
    
    >>> page.restrictedTraverse('@@edit')
    Traceback (most recent call last):
    ...
    Unauthorized: You are not allowed to access '@@edit' in this context

Make sure notallowed css class is applied to edit tab
since we don't have permissions to edit::
    >>> html = page.restrictedTraverse('@@view')()
    >>> 'oc-notallowed' in html
    True

Test wiki history registrations::

    >>> page.restrictedTraverse('history')
    <...SimpleViewClass ...wiki-history.pt object at ...>

    >>> page.restrictedTraverse('version')
    <...SimpleViewClass ...wiki/wiki-previous-version.pt object at ...>

    >>> page.restrictedTraverse('version_compare')
    <...SimpleViewClass ...wiki/wiki-version-compare.pt object at ...>

... and permission

    >>> from AccessControl.SecurityManagement import newSecurityManager
    >>> from AccessControl.User import nobody
    >>> newSecurityManager(None, nobody)
    >>> history = page.restrictedTraverse('history')
    >>> history()
    '... There are no previous versions...

Test wiki attachment registrations which are not used any more::

    >>> page.restrictedTraverse('@@updateAtt')
    Traceback (most recent call last):
    ...
    Unauthorized: You are not allowed to access '@@updateAtt' in this context

    >>> page.restrictedTraverse('@@createAtt')    
    Traceback (most recent call last):
    ...
    Unauthorized: You are not allowed to access '@@createAtt' in this context

    >>> page.restrictedTraverse('@@deleteAtt')    
    Traceback (most recent call last):
    ...
    Unauthorized: You are not allowed to access '@@deleteAtt' in this context

Test logged in user::

    >>> self.loginAsPortalOwner()

Test wiki page registrations (logged in)::

    >>> page.restrictedTraverse('@@view')
    <...SimpleViewClass from ...wiki/wiki-view.pt object at ...>
    
    >>> page.restrictedTraverse('@@wiki_macros')
    <...SimpleViewClass ...wiki/wiki_macros.pt object at ...>
    
    >>> page.restrictedTraverse('@@edit')
    <Products.Five.metaclass.WikiEdit object at ...>

Make sure notallowed css class is not applied to edit tab
since we do have permissions to edit::
    >>> html = page.restrictedTraverse('@@view')()
    >>> 'oc-notallowed' in html
    False

Test wiki history registrations (logged in)::

    >>> page.restrictedTraverse('history')
    <Products.Five.metaclass.SimpleViewClass from ...wiki-history.pt object at ...>

    >>> page.restrictedTraverse('version')
    <Products.Five.metaclass.SimpleViewClass ...wiki/wiki-previous-version.pt object at ...>

    >>> page.restrictedTraverse('version_compare')
    <Products.Five.metaclass.SimpleViewClass from ...wiki-version-compare.pt object at ...>

   
Test wiki attachment registrations (logged in)::

    >>> page.restrictedTraverse('@@updateAtt')
    <Products.Five.metaclass.AttachmentView object at ...>

    >>> page.restrictedTraverse('@@createAtt')    
    <Products.Five.metaclass.AttachmentView object at ...>

    >>> page.restrictedTraverse('@@deleteAtt')    
    <Products.Five.metaclass.AttachmentView object at ...>


Attachments
===========

Test actually creating, editing, deleting an attachment::

     >>> import os, hmac, sha, base64, re
     >>> from urllib import quote
     >>> secret_file_name = os.environ.get('TOPP_SECRET_FILENAME', '')
     >>> if not secret_file_name:
     ...    secret_file_name = os.path.join(os.environ.get('INSTANCE_HOME'), 'secret.txt')
     
     >>> len(secret_file_name) > 0
     True
     >>> os.path.exists(secret_file_name)
     True
     >>> f = open(secret_file_name)
     >>> secret = f.readline().strip()
     >>> f.close()
     >>> len(secret) > 0
     True

Error case for creating an attachment with no attachment there::

     >>> request = self.portal.REQUEST
     >>> view = page.restrictedTraverse('@@edit')
     >>> view.create_attachment()
     {'An error': ''}

Create an attachment to upload::

     >>> class tempfile(file):
     ...     def __init__(self, filename):
     ...         self.filename = filename 
     ...         file.__init__(self, filename)
     >>> tfile = tempfile(secret_file_name)

     >>> form = {}
     >>> form['attachmentTitle'] = 'secret'
     >>> form['attachmentFile'] = tfile
     >>> request.form = form
     >>> view.create_attachment()
     {...'oc-wiki-attachments'...}
     >>> newatt = view.context._getOb('secret.txt')
     >>> newatt
     <FileAttachment at /plone/projects/p1/project-home/secret.txt>
     >>> newatt.Title()
     'secret'

Now let's try to delete.  Try the error case::

     >>> request.form = {}

It raises a TypeError for now, but should eventually return an error message instead::

     >>> view.delete_attachment()
     Traceback (most recent call last):
     ...
     TypeError...

Send in valid attachment id and it should work::

     >>> form = {}
     >>> view.delete_attachment(['secret.txt'])
     {'secret.txt_list-item':...'delete'...}

If we create an attachment with no title, the title should be the id::

     >>> tfile = tempfile(secret_file_name)
     >>> form = {'attachmentFile': tfile}
     >>> request.form = form
     >>> view.create_attachment()
     {...'oc-wiki-attachments'...}
     >>> newatt = view.context._getOb('secret.txt')
     >>> newatt
     <FileAttachment at /plone/projects/p1/project-home/secret.txt>
     >>> newatt.Title()
     'secret.txt'

Test update attachment... first check error case::

     >>> request.form = {}
     >>> view.update_attachment()
     {}

Try again with real values, should work great now::

     >>> view.update_attachment(['secret.txt'], [{'title': "Alcibiades"}])
     {'secret.txt_list-item':...Alcibiades...}


VERSION COMPARE
===============

Now let's exercise some version compare stuff

Verify that a redirect is raised on invalid input

Set up the right view
     >>> view = self.portal.unrestrictedTraverse('projects/p1/project-home/version_compare')
     >>> view
     <Products.Five.metaclass.SimpleViewClass from ...wiki-version-compare.pt object at ...>

Call it with no arguments
     >>> response = view()
     Traceback (most recent call last):
     ...
     Redirect: http://nohost/plone/projects/p1/project-home/history
     >>> 'You did not check any versions in the version compare form' in view.portal_status_message
     True

Reset the request
     >>> request = view.request.form = {}

Try it with just one argument
     >>> request['version_id'] = '0'
     >>> response = view()
     Traceback (most recent call last):
     ...
     Redirect: http://nohost/plone/projects/p1/project-home/history
     >>> 'You did not check enough versions in the version compare form' in view.portal_status_message
     True

Try with 2 arguments, but the versions don't exist
     >>> request['version_id'] = ['0', '1']
     >>> response = view()
     Traceback (most recent call last):
     ...
     Redirect: http://nohost/plone/projects/p1/project-home/history
     >>> 'Invalid version specified' in view.portal_status_message
     True

Try with more than 2 versions
     >>> request['version_id'] = ['0', '1', '2']
     >>> response = view()
     Traceback (most recent call last):
     ...
     Redirect: http://nohost/plone/projects/p1/project-home/history
     >>> 'You may only check two versions in the version compare form' in view.portal_status_message
     True

Now edit 2 pages, so we can try a valid compare later
     >>> request['version_id'] = ['0', '1']
     >>> repo = view.get_tool('portal_repository')
     >>> page.processForm(values=dict(text='some new text'))
     >>> repo.save(page, comment='new comment')
     >>> page.processForm(values=dict(text='some even newer text'))
     >>> repo.save(page, comment='newest comment')

Now we should get a valid response
     >>> response = view()

Test that we can create a page via wicked
     >>> view = page.restrictedTraverse('@@wickedadd')
     >>> view
     <Products.Five.metaclass.WickedAdd object at ...>

     >>> request = self.portal.REQUEST 
     >>> request.form = {'Title' : 'newpage', 'section' : 'text'}
     >>> view()
     'http://...projects/p1/newpage/edit...'

