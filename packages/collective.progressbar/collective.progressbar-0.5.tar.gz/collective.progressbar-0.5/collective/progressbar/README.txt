This product provides a basic html and javascript progress bar that are
useful for long running server side processes like imports or exports.

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


--------------------
Author and Copyright
--------------------

Authors: 

- Roché Compaan <roche@upfrontsystems.co.za>
- Hedley Roos <hedley@upfrontsystems.co.za>

Copyright (C) 2009 Upfront Systems, Stellenbosch, South Africa

-------
License
-------

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


 
