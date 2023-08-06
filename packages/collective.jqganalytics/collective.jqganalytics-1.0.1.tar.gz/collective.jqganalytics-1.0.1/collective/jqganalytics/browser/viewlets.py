from plone.app.layout.viewlets.common import ViewletBase
from zope.component.interfaces import ComponentLookupError
from zope.component import getUtility

from collective.jqganalytics.interfaces import IGoogleAnalyticsConfiguration



class TrackPageViewlet(ViewletBase):
    def update(self):
        try:
            config = getUtility(IGoogleAnalyticsConfiguration)
            self.account_id = config.account_id
        except ComponentLookupError:
            self.account_id = None
            pass
    
    def index(self):
        if self.account_id:
            return """
                <script type=\"text/javascript\">
                    jQuery.trackPage('%s');
                </script>""" % (self.account_id)
        
        return ""
