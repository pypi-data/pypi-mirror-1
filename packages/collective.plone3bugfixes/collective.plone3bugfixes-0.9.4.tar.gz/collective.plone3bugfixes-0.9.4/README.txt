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
    - Fix livesearch. The "show all" and the "advanced search" links linked
      to the current context, which produces very small search results, because
      search is context sensitive. Now, the portal_url is used for the link.
      This was a bug, because the live-search IS NOT context sensitive usually.
    - Removed the advanced search ("search_form") completely and traverse to search.
      This is because the search_form is just broken. It shows all portal_types
      even if they're configured not to be searched. This is especially ugly if you
      use ploneformgen or topics.
    - Fixed translation for batch_x_items_matching_your_criteria. Broken at least since 3.0 ("fuzzy").


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
