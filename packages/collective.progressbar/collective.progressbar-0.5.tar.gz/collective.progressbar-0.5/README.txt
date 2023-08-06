collective.progressbar
======================

This product provides a basic html and javascript progress bar for Plone
that are useful for long running server side processes like imports or
exports.

To use it, you simply have to fire two events. The first event
initialises the progress bar view:

    from collective.progressbar.events import InitialiseProgressBar
    from collective.progressbar.events import ProgressBar

    title = 'Importing file'
    bar = ProgressBar(self.context, self.request, title)
    notify(InitialiseProgressBar(bar))

The ProgressBar class above can take an optional view parameter if you
want to customise the view that renders the progress bar further. You
only have to include the progressbar macro in your custom view.

To update progress, you simply have to fire the appropriate event:

    from collective.progressbar.events import UpdateProgressEvent
    from collective.progressbar.events import ProgressState

    for index in range(101):
        progress = ProgressState(self.request, index)
        notify(UpdateProgressEvent(progress))

To see how the progress bar works, install the package and browse to the
demo view eg.: http://localhost:8080/plone/@@collective-progressbar-demo


Authors and Copyright
---------------------

Authors: 

- Roche Compaan <roche at upfrontsystems.co.za>
- Hedley Roos <hedley at upfrontsystems.co.za>

Copyright (C) 2009 Upfront Systems, Stellenbosch, South Africa
