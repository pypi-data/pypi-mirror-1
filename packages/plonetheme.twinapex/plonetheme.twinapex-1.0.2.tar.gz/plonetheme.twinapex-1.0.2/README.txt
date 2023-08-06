Twinapex Theme is a theming product for Plone to give your site a professional corporate look. Some 
functional features are included - e.g. option to set header images for all content.

Features
--------

* 1000 px fixed width layout

* Dropdown menus

* Header images (per page) can be changed by the content editor

* Header flash animations (per page) can be changed by the content editor

* Through-the-web editing of footer links

* `Body text in RSS <http://rudd-o.com/en/linux-and-free-software/a-hack-to-enable-full-text-feeds-in-plone>`_

* Multilingual. Built-in Finnish and English support

Preface
-------

Requirements
------------

Plone 3.x series. Tested against Plone 3.1.x and Plone 3.3rc4.

* LinguaPlone 2.4.x language viewlet is used on multilingual sites.

* archetypes.schemaextender product is used 

Installation
------------

`Follow generic instructions for installing egg-based add-on <http://plone.org/documentation/tutorial/third-party-products>`_.
`Follow these guidelines if you need to ask help regarding installation problems <http://plone.org/documentation/how-to/diagnosing-third-party-product-installation-problems>`_.

After installing, depending on your configuration you might want to rearrange and show/hide viewlets. Use
http://yoursite/@@manage-viewlets link for this.

Example buildout.cfg
====================

See below::

	eggs =
		...
	    plonetheme.twinapex
	    
	zcml =
		...
	    webcouturier.dropdownmenu
	    plonetheme.twinapex

Example sites
-------------

* http://www.twinapex.com

* http://www.twinapex.fi

Quality assurance
-----------------

- Tested with IE6, IE7, Firefox 3.x and Google Chrome

Other
-----

See also `Freearch Theme <http://plone.org/products/free-arch-theme>`_.

Author
------

`Twinapex Team - Professional Python and Plone hackers for hire. <mailto:info@twinapex.com>`_. 

* `Twinapex company site <http://www.twinapex.com>`_ (`Finnish <http://www.twinapex.fi>`_)

* `Twinapex company blog <http://blog.twinapex.fi>`_

* `Twinapex mobile site <http://www.twinapex.mobi>`_

* `More about Plone <http://www.twinapex.com/products/plone>`_

* `Other open source Plone products by Twinapex <http://www.twinapex.com/for-developers/open-source/for-plone>`_

Changelog
---------

1.0.1 - 1.0.2
=============

Fixed missing : character in README.txt. The world should seriously consider reST validators. 

1.0 - 1.0.1
===========

Fixed packaking scripts and included missing files.
 


