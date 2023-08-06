from StringIO import StringIO
from datetime import datetime

from zope.interface import implements
from zope.component import getUtilitiesFor

from Products.CronUtility.interfaces import ICronUtility, ICron

class CronUtility(object):
    """cron-registry"""
    implements(ICronUtility)

    def getCrons(self):
        """get all registered cron-utilities"""
        utilities = []
        for utility in getUtilitiesFor(ICron):
            if utility is not None:
                utilities.append(utility)
        return utilities

    def runCrons(self, context, debug=0):
        """run all active crons"""
        out = StringIO()
        res = StringIO()
        dt = datetime.now()
        for name, utility in self.getCrons():
            if utility.active(dt) or debug:
                cdt = datetime.now()
                cout = utility.run(context)
                if cout:
                    print >> out, '@ %s: starting cron %s' % (cdt, name)
                    print >> out, cout
                    print >> out, '@ %s: finished cron %s' % (datetime.now(), name)
        if out.getvalue():
            print >> res, '@ %s: starting crons' % dt
            print >> res, out.getvalue()
            print >> res, '@ %s: finished crons' % datetime.now()
        else:
            print >> res, 'no active crons'
        return res.getvalue()

