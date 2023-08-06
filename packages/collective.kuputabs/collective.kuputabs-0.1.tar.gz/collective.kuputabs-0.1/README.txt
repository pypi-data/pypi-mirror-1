Introduction
============

Kupu Tabs enables end user editable plone.org like front page tabs in WYSIWYG editors.

This is a generic Javascript/CSS library and can be pluggd in to any WYSIWYG editor. Currently Kupu is supported.

Benefits and use cases
======================

* Where there is plenty of content on the page, but splitting it up is unsuitable and we do not want the user navigate away from the page

* Suitable for content where the reading order is not critical

* No page loads - better user experience

* Fact pages (http://plone.org front page)

* Data sheets

* Accessibility - if Javascript is not supported renders as a normal page

* Printability - prints as a normal page

Installation
============

Install via buildout

eggs =
	collective.kuputabs
	
zcml =
	collective.kuputabs
	
Usage - Plone
=============

Open any Kupu editable content.

Write a tab name and choose "Tab" as its style from Kupu style drop down.

All text after Tab until the next Tab section or the end will be placed inside a tab container. 
Tab'ed text will be placed inside a tab container.

You can choose which tab is open by default with Tab (open by default) style.

There is two example style files: kuputabs.css.dtml for any Plone theme (variable colors) and kuputabs2.css which
is more generic one.

Usage - Generic HTML
====================

Create a container DIV for your content. Usually this is #content or similar and already provided your CMS/blog/whatever.

Add class "kuputab-tab-definer" for <h2> elements you want to be tabs. Add class "kuputab-tab-definer-default" for 
the tab which is open by default.

Include kuputabs.js on your page. Include kuputabs-alternative.css stylesheet or create your own. 

Voila.


Under the hood
==============

When the page is loaded in the view mode, Javascript parses all kuputabs-tab sections and builds a tab container from them.
If Javascript is disabled the content will appear under normal Subheading styles.

There is an important distinction with two kind of CSS classes

- kuputab-tab-definer is h2 element which marks the beginning of the tab

- all content until the end of kuputab-tab-definer parent element or next kuputab-tab-definer goes to this tab

- kuputab-tab-definer content is mutated to kuputab-tab-container which is placed at the bottom of kuputab-tab-definer container element

document.designMode attribute is used to determine whether the visitor views the page or is it under WYSIWYG editor.

Author
======

Mikko Ohtamaa

`Twinapex Research, Oulu, Finland <http://www.twinapex.com>`_ - High quality Python hackers for hire


Sponsorship
===========

Thanks to our fabulous sponsors.

 `London School of Marketing <http://londonschoolofmarketing.com>`_.









