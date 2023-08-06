from zope import interface

class ICronUtility(interface.Interface):
    """cron-utility"""

    def getCrons():
        """get all registered cron-utilities"""

    def runCrons():
        """run all active crons"""

class ICron(interface.Interface):
    """cron"""

    def active(datetime):
        """checks if the cron is active"""

    def run(context):
        """this method is executed if the cron is active"""