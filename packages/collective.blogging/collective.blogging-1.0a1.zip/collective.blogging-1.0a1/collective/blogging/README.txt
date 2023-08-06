About
============

Yet another blogging tool for Plone. Blogging package provides simple extension for Plone
to make blogging easier with as little as possible modifications or extra content.
But still use as much as possible from Plone's default UI to let user's get familiar
with extra blogging features in a while.

Installing
============

This package requires Plone 3.x or later (tested on 3.3.x).

Installing without buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install this package in either your system path packages or in the lib/python
directory of your Zope instance. You can do this using either easy_install or
via the setup.py script.

Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using `buildout`_ to manage your instance installing
collective.blogging is even simpler. You can install
collective.blogging by adding it to the eggs line for your instance::

    [instance]
    eggs = collective.blogging

After updating the configuration you need to run the ''bin/buildout'', which
will take care of updating your system.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

Usage
=====

So, let's say that in most cases when you want to start simple personal blog,
default Plone installation without any extra add-ons provides almost all you need.
For example you can create Folder / Large Plone Folder for blog posts, Smart Folder
as site frontpage with criteria to search contents of the blog folder and then you
can start blogging by creating News Items in the blog folder.

Yes that's fine but after while you end up with thinking about better blog view
template because folder summary view doesn't provide some extra info about listed
News Items like number of comments, permalink etc.

And that's why the Blogging package was created and hopefully will save your time
in case you don't need complex blogging tool but still want a blog.

Features
========

- Creating blog(s) from Plone Folders

- Posting Plone's Pages, News Items, Files, Images, Links and External Videos (or other embed content)

- Smart folders supported

- Fancy image galleries

- Simple archive toolbar (filter by category, year, month)

- Helper blog portlet

- Next / Prev navigation replacement

- User's guide included in the UI (localizable)

For more information how to use blogging features go to [your-site]/blogging-help.

Translations
============

- English (default): lzdych (lukas dot zdych at gmail dot com)

- Czech: lzdych (user's guide not translated yet)

New translations or help with correction of an existing ones would be appreciated.

Examples
========

Here are sites where the blogging tool is already in production use.

- lukaszdych.net_

.. _lukaszdych.net: http://lukaszdych.net

Copyright and Credits
=====================

collective.blogging is licensed under the GPL. See LICENSE.txt for details.

Author: `Lukas Zdych (lzdych)`__.

.. _lzdych: mailto:lukas.zdych@gmail.com

__ lzdych_

Homepage: collective.blogging_.

.. _collective.blogging: http://plone.org/products/collective.blogging
