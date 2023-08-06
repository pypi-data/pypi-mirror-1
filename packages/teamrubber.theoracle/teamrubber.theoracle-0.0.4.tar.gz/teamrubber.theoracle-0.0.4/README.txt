Introduction
============

The Oracle is a debug/development helper app for Plone.  It currently shows 
the following information about a given user/context:

* Authenticated User Info - ID, member type, roles, etc.
* Authenticated User Attributes
* Basic Context Info - ID, portal type, path, absolute url, etc.
* Context Workflow Info - Review state, history, assigned workflow
* Catalog Indexes
* Catalog Metadata
* Methods - view source and call those without arguments
* Attributes and their values
* Valid/Invalid permissions
* Context source code

It also provides a fast way to drop to PDB at any given context.

Installation/Use
================

To install, just stick it in your buildout, once you've got your instance
running, there's a few of views which you can use:

* the_oracle - Main context inspection tool
* pdb - Drops you to pdb at the current context
* the\_oracall - Allows you to call methods on objects. Doesn't support
 				arguments yet. eg /the\_oracall?method=__makeFire
* the\_oracode - See the source of a given method.
				eg /the\_oracode?method=reindexObject

A Friendly Warning
==================

Don't leave this product installed on a production site, or anywhere near 
production data. It massively undermines the security of the site it's 
installed on and allows you wreck a site and data in all kinds of new and 
exciting ways.  Also, angry bears with assault rifles will come to your 
house and rough you up if you do. Seriously. They're not happy bears at all.
