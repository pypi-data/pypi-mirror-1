from plone.app.layout.viewlets.common import ViewletBase
from zope.component.interfaces import ComponentLookupError
from zope.component import getUtility

from Products.CMFCore.Expression import getExprContext

from collective.jqganalytics.interfaces import IGoogleAnalyticsConfiguration



class TrackPageViewlet(ViewletBase):
    account_id = None
    variables = u''
    
    def update(self):
        try:
            config = getUtility(IGoogleAnalyticsConfiguration)
        except ComponentLookupError:
            return
        
        self.account_id = config.account_id
        econtext = getExprContext(self.context)
        self.variables = u'\n'.join(map(lambda v: v.render(econtext),
                                        filter(lambda v: v.available(econtext),
                                               config.custom_variables)))
    
    def index(self):
        if self.account_id:
            return """
                <script type=\"text/javascript\">
                    jQuery.pageTrackerLoaded(function() {
                        var pageTracker = jQuery.getPageTracker();
                        %(variables)s
                        jQuery.trackPageview();
                    });
                    jQuery.loadPageTracker('%(account_id)s');
                </script>""" % (self.__dict__)
        
        return ""
