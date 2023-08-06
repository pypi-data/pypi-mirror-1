from zope.component.interfaces import ObjectEvent
from zope.interface import implements, Interface

from interfaces import IInitialiseProgressBar, IUpdateProgressEvent

# events
class InitialiseProgressBar(ObjectEvent):

    implements(IInitialiseProgressBar)


class UpdateProgressEvent(ObjectEvent):

    implements(IUpdateProgressEvent)


# progress bar
class ProgressBar(object):

    def __init__(self, context, request, title, description, view=None):
        self.context = context
        self.request = request
        self.title = title
        self.description = description
        self.view = view


# progress state
class ProgressState(object):

    def __init__(self, request, progress):
        self.request = request
        self.progress = progress


# event handlers
def init_progress_bar(bar, event):
    view = bar.view
    if view is None:
        view = bar.context.restrictedTraverse('@@collective.progressbar')

    view.title = bar.title
    view.description = bar.description

    bar.request.response.write(view().encode('utf-8'))


def update_progress(state, event):
    state.request.response.write(
        '<input style="display: none;"'
        ' name="_progress" value="%s">' % state.progress)

