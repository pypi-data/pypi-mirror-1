from Acquisition import aq_inner
from zope.component import queryUtility

from Products.Five.browser import BrowserView

from Products.CronUtility.interfaces import ICronUtility

class CronRunner(BrowserView):
    """runs the registered crons
    """

    def __call__(self):
        context = aq_inner(self.context)
        if not self.request.get('REMOTE_ADDR', None) == '127.0.0.1':
            return "unauthorized"
        registry = queryUtility(ICronUtility)
        if registry is not None:
            return registry.runCrons(context, debug=self.request.get('debug', 0))
        return "cron utility not found"