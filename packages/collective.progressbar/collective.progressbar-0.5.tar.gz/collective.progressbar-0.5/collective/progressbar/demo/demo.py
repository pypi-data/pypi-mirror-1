import time
from Products.Five import BrowserView
from zope.event import notify

from collective.progressbar.events import InitialiseProgressBar
from collective.progressbar.events import ProgressBar
from collective.progressbar.events import UpdateProgressEvent
from collective.progressbar.events import ProgressState

class DemoProgressBar(BrowserView):
    """ Demo progress bar
    """

    def __call__(self):
        bar = ProgressBar(self.context, self.request, 'Demo Progress Bar',
            'Demo in progress ...')
        notify(InitialiseProgressBar(bar))

        for index in range(101):
            progress = ProgressState(self.request, index)
            notify(UpdateProgressEvent(progress))
            time.sleep(1)
