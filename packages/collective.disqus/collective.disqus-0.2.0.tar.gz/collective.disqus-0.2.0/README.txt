Introduction
============

Integrates `DISQUS`_ comment system with `Plone`_.

Default Plone discussion mechanism doesn't have nice panel to administer
comments. It's hard to find new comments. It's not possible to block
posts with links or some other unwelcome contents.

But on the web there are much more specialized tools for commenting:

* `JS-Kit`_
* `DISQUS`_
* `IntenseDebate`_

This comments system can be easyly integrated with sites - user just need
to create account and add some special code into his website.

collective.disqus integrates `DISQUS`_ comment system with `Plone`_.


Installation
============

It's only few easy steps to integrate DISQUS with your Plone site:

* create account on `DISQUS`_
* add you website in DISQUS admin panel (remember configured website short name)
* install `collective.disqus`:
  
  add to your buildout::

    eggs =
      collective.disqus

  use *Add products* in *Site Setup* or *QuickInstaller* to activate it

Current version of `collective.disqus` doesn't migrate comments. So all
comments that was created before installation will be hidden (not removed).


Configuration
=============

Go to *Site Setup* -> *DISQUS comment system* control panel form and configure *Website short name*.
DISQUS should be visible in all contents that enabled commenting.


Contributors
============

Project initiated by `Wojciech Lichota`_.

Contributors:

* Wojciech Lichota [sargo]


.. _DISQUS: http://disqus.com
.. _Plone: http://plone.org
.. _Wojciech Lichota: http://lichota.pl
.. _JS-Kit: http://js-kit.com/
.. _IntenseDebate: http://intensedebate.com/home
