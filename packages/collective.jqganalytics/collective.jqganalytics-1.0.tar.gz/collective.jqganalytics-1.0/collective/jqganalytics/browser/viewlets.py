from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getUtility

from collective.jqganalytics.interfaces import IGoogleAnalyticsConfiguration



class TrackPageViewlet(ViewletBase):
    def update(self):
        config = getUtility(IGoogleAnalyticsConfiguration)
        self.account_id = config.account_id
    
    def index(self):
        return """
            <script type=\"text/javascript\">
                jQuery.trackPage('%s');
            </script>""" % (self.account_id)
