collective.skinny
=================

An example implementation of a separate, public-facing skin as
discussed at:

- http://danielnouri.org/blog/devel/zope/plone-3-theming-for-mortals-part2.html
- http://danielnouri.org/blog/devel/zope/plone-3-theming-for-mortals.html
- http://weblion.psu.edu/news/viewlets-barriers-for-plone-newbies

Look at the package's ``configure.zcml`` file for instructions on how
to activate the public skin to actually see it.

You can use this package either as a template to copy and modify, or
use it as it is and extend within your own package.

If you decide to extend this with your own package, which is probably
the cleaner way of doing it, You can start out by overriding the
``index.html`` view, and thus the ``main.Main`` class in your
``overrides.zcml`` file, using directives as you find them in them in
this package's ``configure.zcml``.  You can then subclass the
``main.Main`` browser view and code away.
