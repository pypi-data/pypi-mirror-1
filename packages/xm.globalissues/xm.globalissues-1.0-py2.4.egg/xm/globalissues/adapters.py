from zope import component

class GlobalIssueGetter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal_tools = component.getMultiAdapter((context, request), name="plone_tools")
        self.catalog = self.portal_tools.catalog()


    def get_issues(self, **kwargs):
        """Get a list of issue brains.

        This implementation will get all issues in the instance which are 
        in-progress or unconfirmed

        """
        query = dict(portal_type='PoiIssue',
                     review_state=['in-progress', 'open',
                                   'unconfirmed', 'new'],
                     path='/')
        query.update(kwargs)
        return self.catalog(**query)
