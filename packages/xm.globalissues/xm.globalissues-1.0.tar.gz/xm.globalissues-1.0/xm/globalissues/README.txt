===============
xm.globalissues
===============

eXtremeManagement has a content type called 'Poi Task' that provides a way to link a
task to a story.

xm.globalissues changes the way issues are being found when adding a
Poi Task, so issues are found globally in the instance.

Setup
=====

  >>> self.setRoles(['Manager'])
  >>> workflow = self.portal.portal_workflow

We need to install Poi and eXtremeManagement:

  >>> ignore = self.portal.portal_quickinstaller.installProducts(['Poi', 'eXtremeManagement'])

We create a project, an iteration, and a story.  Note that in our
model, issues correspond to tasks:

  >>> projectfolder = \
  ...     self.portal[self.portal.invokeFactory('Folder', 'folder')]
  >>> project = projectfolder[projectfolder.invokeFactory('Project', 'project')]
  >>> iteration1 = project[project.invokeFactory('Iteration', 'iteration1')]
  >>> story1 = iteration1[iteration1.invokeFactory('Story', 'story1')]

Remember that a story has to be estimated and marked as so, so that
we're able to add any tasks to it.  Therefore, right now, we shouldn't
be able to add any tasks. An image is allowed, though.

  >>> def list_addable(context):
  ...     allowed = context.getAllowedTypes()
  ...     addable = context.getAddableTypesInMenu(allowed)
  ...     return u', '.join(ad.Title() for ad in addable)
  >>> list_addable(story1)
  u'File, Image'

  >>> story1.setRoughEstimate(1.5)
  >>> workflow.doActionFor(story1, 'estimate')
  >>> list_addable(story1)
  u'File, Image, Issue Tracker Task, Task'

Let's create an issue tracker in the project with two issues in it:

  >>> tracker = project[project.invokeFactory('PoiTracker', 'tracker')]
  >>> myissue = tracker[tracker.invokeFactory('PoiIssue', '1')]
  >>> yourissue = tracker[tracker.invokeFactory('PoiIssue', '2')]

Poi Tasks
=========

In our story, we can now add two different types of tasks, the normal
"Task" type and the "Poi Task" type.  The "Poi Task" is what we're
interested in, so let's create one and connect it with one of our
issues:

  >>> task = story1[story1.invokeFactory('PoiTask', 'task')]
  >>> task.setIssues([myissue])
  >>> task.getIssues()
  [<PoiIssue at /plone/folder/project/tracker/1>]
  >>> story1.manage_delObjects(['task'])

Poi Tasks have a vocabulary method `vocabulary_issues` that'll return
a DisplayList of issues that can be referred to.  Note that this list
only includes open issues:

  >>> task.vocabulary_issues() # doctest: +ELLIPSIS
  <DisplayList [('...', '#1: '), ('...', '#2: ')] at ...>
  >>> myissue.isValid = True
  >>> workflow.doActionFor(myissue, 'post')
  >>> workflow.doActionFor(myissue, 'resolve-unconfirmed')
  >>> task.vocabulary_issues() # doctest: +ELLIPSIS
  <DisplayList [('...', '#2: ')] at ...>
  >>> workflow.doActionFor(myissue, 'open-resolved')
  >>> task.vocabulary_issues() # doctest: +ELLIPSIS
  <DisplayList [('...', '#1: '), ('...', '#2: ')] at ...>

Mass-creating Poi Tasks
-----------------------

The `@@xm-poi` view allows us to create tasks by tags.  We use the
`add_tasks_from_tags` method for this.

  >>> from Products.statusmessages.interfaces import IStatusMessage
  >>> storyview = story1.restrictedTraverse('@@xm-poi')
  >>> def show_message():
  ...     for msg in [msg.message for msg in
  ...                 IStatusMessage(storyview.request).showStatusMessages()]:
  ...         print msg


Finding issues globally
-----------------------

Thanks to xm.globalissues, issues that live outside our project are also
considered:

  >>> folder = self.folder
  >>> tracker2 = folder[folder.invokeFactory('PoiTracker', 'tracker2')]
  >>> other_issue = tracker2[tracker2.invokeFactory('PoiIssue', 'other-issue')]
  >>> other_issue.setSubject(['yourtag'])
  >>> other_issue.reindexObject()
  >>> storyview.add_tasks_from_tags(['yourtag'])
  >>> show_message() # doctest: +NORMALIZE_WHITESPACE
  Added tasks for issues: other-issue.
