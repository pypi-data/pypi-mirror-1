gomobile.xhtmlmp provides XHTML mobile profile cleaner. It takes in arbitary HTML code
and turns it to valid XHTML-MP code which can be dropped in XHTML MP page. 

The code will also filter possible malicious code in external feed content, like <script> tags.

Requirements
------------

* Python 2.4

* `lxml <http://pypi.python.org/pypi/lxml/>`_

This package has no dependencies to Plone or GoMobile and can be used with any Python code.

Features
--------

* Turn any incoming HTML/XHTML to mobile profile compatible

  * Enforce ALT text on images - especially useful for external tracking images (feedburner tracker)

* Protect against Cross-Site Scripting Attacks (XSS) and other nastiness, as provided by 
  `lxml.html.clean  <http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html>`_  

* Unicode compliant - eats funky characters


Usage
-----

clean_xhtml_mp(html)
====================

This function will do everyhing you need.

Run XHTML mobile profile cleaner for HTML code::
        
	@param html: HTML as a string or lxml Document        
	@return: XHTML, utf-8 encoded string
	
Example::

	from gomobile.xhtmlmp.transformers.xhtmlmp_safe import clean_xhtml_mp

	html = '<img src="http://www.foobar.com">'
	output = clean_xhtml_mp(html)        
	self.assertEqual(output, '<img src="http://www.foobar.com" alt=""/>', "Got:" + output)
    
   
Roadmap
-------

Future features will include:

* Automatic resize for image sources

Unit tests
----------

Put gomobile.xhtmlmp to your PYTHONPATH.

Run unit tests normally like:: 

	python tests/test_image.py

See also
--------

* `Plone GoMobile project <http://pypi.python.org/pypi/gomobile.mobile/>`_

* http://en.wikipedia.org/wiki/XHTML_Mobile_Profile

* http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html

* `W3C XHTML mobile validator <http://validator.w3.org/mobile/>`_

* `mobiReady <http://mobiready.com/>`_

Author
------

`Twinapex Team - Professional Python and Plone hackers for hire. <mailto:info@twinapex.com>`_. 

* `Twinapex company site <http://www.twinapex.com>`_ (`Finnish <http://www.twinapex.fi>`_)

* `Twinapex company blog <http://blog.twinapex.fi>`_

* `Twinapex mobile site <http://www.twinapex.mobi>`_

* `More about Plone <http://www.twinapex.com/products/plone>`_

* `Other open source Plone products by Twinapex <http://www.twinapex.com/for-developers/open-source/for-plone>`_  

