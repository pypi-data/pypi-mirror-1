Introduction
============

Plone3 has many annoying style bugs. This package tries to fix as many as possible.

The included fixes are:

    - Remove "* html" hacks from IEFixes.css to allow IE7 and IE8 to benefit
      from the fixes there.
    - Add the IE7ish behavour declaration into the main template to have IE8 to
      behave like IE7
    - Fix the order of the resourceregistries to have js after css to have a
      beautiful rendering in Firefox and to have a _real_ DomReady event in JS.

Reasons
=======

The reason why we don't write bugreports is that nobody seems to care about them.
Yes, we tried before.


Tested Plone Versions
=====================

    - 3.0
    - 3.1
    - 3.2

Authors
=======

    - Oliver Roch <oliver.roch@brainson.de>
    - Daniel Kraft <daniel.kraft@d9t.de>
