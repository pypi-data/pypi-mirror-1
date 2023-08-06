Introduction
============

qi.xmpp.botfarm is a twisted based server that provides xmlrpc services to manage a collection of jabber-based helpdesks. It is currently used at chatblox.com_.

.. _chatblox.com: http://chatblox.com

Installation
============

Installing with buildout
------------------------
        
If you are using `buildout`_ to manage your instance installing qi.xmpp.botfarm is very simple. You can install it by adding a new section, botfarm and include it in the parts section::

[botfarm]
recipe = zc.recipe.egg
eggs = qi.xmpp.botfarm
	qi.xmpp.client
	qi.xmpp.admin


A link will be created in the bin directory pointing to the botfarm executable. 

.. _buildout: http://pypi.python.org/pypi/zc.buildout

Installing without buildout
---------------------------

You can install qi.xmpp.botfarm easily using the easy_install command from setuptools. This will also install dependencies.

Usage
=====
botfarm is called with the path to an xml configuration file as an argument. Copy config.xml in the docs folder and customize to your needs.

