Introduction
============
CAPTCHA has a number of disadvantages such as usability and possibly the false sense of security. As white papers documenting the easy cracking of CAPTCHA become more prevalent, the security issues have been growing in concern.

Products.humanator relies on a different method of determining if the user is human or not. Rather than rely on images (and audio), the humanator widget asks the user questions such as::

  What is six plus 9?

  Type the word 'human' in all capital letters.

  What is the best programming language of all time?

The user provides the correct answer and the form is then validated.

These questions are created by the content editor and are stored as a custom content object simply called HumanatorQuestions. The widget does a randomized portal catalog search and serves that to the user. I'm considering creating a number of stock number of questions stored as fixtures for easy import

Products.humanator has no dependencies.


Installing
----------

This package requires Plone 3.x or later.

Installing without buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install this package in either your system path packages or in the lib/python
directory of your Zope instance. You can do this using either easy_install or
via the setup.py script.

After installing the package it needs to be registered in your Zope instance.
This can be done by putting a Products.humanator-configure.zcml file in the
etc/package-includes directory with this content::

  <include package="Products.humanator" />

or, alternatively, you can add that line to the configure.zcml in a package or
Product that is already registered.

Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using `buildout`_ to manage your instance installing
collective.captcha is even simpler. You can install collective.captcha by
adding it to the eggs line for your instance::

  [instance]
  eggs = Products.humanator
  zcml = Products.humanator

The last line tells buildout to generate a zcml snippet that tells Zope
to configure Products.humanator.

If another package depends on the Products.humanator egg or includes its zcml
directly you do not need to specify anything in the buildout configuration:
buildout will detect this automatically.

After updating the configuration you need to run the ''bin/buildout'', which
will take care of updating your system.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

