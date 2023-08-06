collective.skinny
=================

An example implementation of a separate, public-facing skin as
discussed at:

- http://danielnouri.org/blog/devel/zope/plone-3-theming-for-mortals-part2.html
- http://danielnouri.org/blog/devel/zope/plone-3-theming-for-mortals.html
- http://weblion.psu.edu/news/viewlets-barriers-for-plone-newbies
- http://danielnouri.org/blog/devel/zope/plone-3-theming-for-you.html

Usage
-----

Look at the package's ``configure.zcml`` file for instructions on how
to activate the public skin to actually see it.

This package is both an example and a library.  The easiest way to
start using it is to just copy the package and modify.

The better way is to use it as a library and extend it with your own
package.  When doing so, you'll probably want to start out by
subclassing and overriding through ZCML the main view, which lives in
``main.Main``.  Look at the ``configure.zcml`` file for pointers.

To get started, look at the ``templates/`` directory.  The ``main.pt``
template is where everything is wired together.  You can render other
templates in the same directory by saying ``view/render_spam``, which
will render the ``spam.pt`` template.

Writing views for content objects works similarly.  Look at
``templates/content/document.pt`` to see how this can work.  This
template is found and used because it corresponds to the
``portal_type`` of the content object you're displaying.  Thus, you
can make your own view for Smart Folders by putting a ``topic.pt``
template into the same directory, to give an example.  If no content
view is found, we'll try and display Plone's default view for you.

All of Plone's views such as ``@@plone_context_state`` and friends are
available as usual in templates.  In addition, there's a handy
shortcut for looking up tools: Using ``view/portal_spam`` will return
the ``portal_spam`` tool from your Plone site.  (Try
``view/portal_url`` for a working example ;-).

Screenshot
----------

The example in this package looks something like this:

.. image:: http://danielnouri.org/media/acme-website.png

Feedback
--------

I'd like to make this package work as easy as possible for you.  Let
me know if you have any comments or questions by either using the
comments on `this blog post`_, or by dropping an e-mail to
*daniel.nouri <at> gmail.com*.

.. _this blog post: http://danielnouri.org/blog/devel/zope/plone-3-theming-for-you.html
