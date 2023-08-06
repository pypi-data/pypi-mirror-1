Introduction
============

The sentence "*Plone is slow*" can open a very big dicussion thread.
What is ofter true is this: "*Work with Plone UI is slow*".

The Plone interface need the user to click many times to do (or repeat) common tasks.
This is how the World Wide Web works: click on a link, move to a page, click on another link...

Is clear to all that the presence of Javascript can speed up (sometimes dramatically) the speed
of working with CMS.

What SpeedUpUI Pathbar does
===========================

The common static breadcrumb viewlet of Plone can be replaced with a new one.

Why work with static and poor-of-features links in the pathbar when we can replace those links
with a command interface, to perform directly common operation on the elements inside the pathbar?

So the pathbar will change in a dropdown menu with inside common operation like:

* View the content (what stardard pathbar viewlet does normally)
* Edit the content directly
* Go to *folder_contents* view of the element

All those new features are nothing special right now, but can free the user from performing
additional clicks.

Installation
============

Just register redturtle.speedupui.pathbar in your buildout *.cfg* file.

::

    [instance]
    ...
    eggs =
        ...
        redturtle.speedupui.pathbar
    ...
    
    zcml =
        ...
        redturtle.speedupui.pathbar
		redturtle.speedupui.pathbar-overrides
    ...

TODO
====

* Make possible to **add new portal content** directly from the pathbar
* Check user **permissions** (for edit, see folder contents, ...)
* Dropdown are now done using basic Plone javascript; think about relying on jQuery Tools
  (plone.app.jqtools)
* Memus don't work exactly like the basic dropdown ones. For some reason they don't close
  automatically
* No test with Internet Explorer done right now!

