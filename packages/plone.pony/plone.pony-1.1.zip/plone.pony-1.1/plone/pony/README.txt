Plone Pony
==========

Plone was in need of a pony, so here we go.  Once installed it should
show up on every page:

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.open('http://nohost/plone/')
  >>> browser.contents
  '...Skip to...
   ...*jgs/...
   ...Site Map...
   ...Welcome to Plone...'

  