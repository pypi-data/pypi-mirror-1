================
bda.contentproxy
================

Overview
========

Module providing some flavour of content proxy for Plone. It works for all
kinds of Archetypes based types.
  
Consider that the Archetypes UID must be present in the portal_catalog
(default in plone 3) and the view for the Type must come along with
a ``main`` macro in it's view, i.e.::
  
 <metal:main fill-slot="main">
   <tal:main-macro metal:define-macro="main">
  
   <!-- type view goes here -->
  
   </tal:main-macro>
 </metal:main>
  
This macro is called on the proxied content and is inserted into the ``main``
slot of the ``main_template`` in the current context.
  
Two kinds of proxy behaviour are provided:
  
- A placeless proxy

  This is a simple BrowserView named ``proxy``, with its own
  traverser resolving the trailing part of the URL as the Archetype UID, i.e.::

   http://your.domain.net/some/path/@@proxy/0c6e067822a520eabcfdd1e67d209d96
  
- The other way is a simple Archetype with a UID reference field
  The first kind of proxy may takes place when rendering search results,
  the other one might be used to insert *remote* content to a specified place
  in the folder hirarchy.


KSS
===

Archetypes provides inline editing stuff. Since the proxied content is indeed
rendered as is, the KSS rules for archetypes apply, but on the wrong context,
so we set a condition inside the kssregistry on at.kss resource to determine
wether it should be loaded or not.
  
If you use the proxy not via the placeless proxy or the proxy type, but out
of your own application, you might have to add your own conditional rule to
avoid at.kss to be loaded. This can be done by the IContentProxiedRule
interface.
  
To provide your custom rule, implement this interface and register your object
as multiadapter for context and request, i.e.::
  
 <adapter
   for="foo.bar.interfaces.IBaz
        zope.publisher.interfaces.http.IHTTPRequest"
   factory="foo.bar.baz.Baz"
 />
 
A Base Rule object as well as a default rule object exist in
bda.contentproxy.proxy. The default rule is registered for ``*``. if you want to
provide your own general rule, you have to define your rule implementation in
an overrides.zcml, but its strongly recommended to avoid this due to several
applications registering their own general rules, that might end in confusing
side effects. better bind to the context interface explicit.
  

Installation
============

1. Make the egg available in your instance,

2. Make sure to have ``bda.resultduplexer`` available
  
3. Import the bda.contentproxy extension profile in your plone instance.

This Product is tested with Plone 3.0


Copyright
=========

Copyright 2008, BlueDynamics Alliance, Austria - 
`bluedynamics.com <http://bluedynamics.com>`_


Credits
=======

- Written by `Robert Niederreiter <mailto:rnix@squarewave.at>`_
  Squarewave Computing, BlueDynamics Alliance, Austria
        
- Ideas and contributions: `Jens Klein <mailto:jens@bluedynamics.com>`_
  BlueDynamics Alliance, Klein & Partner KEG, Austria
  
- This addon is an outcome of the UN ILO Better Work project.


Licence
=======

- GNU General Public Licence 2.0 or later

