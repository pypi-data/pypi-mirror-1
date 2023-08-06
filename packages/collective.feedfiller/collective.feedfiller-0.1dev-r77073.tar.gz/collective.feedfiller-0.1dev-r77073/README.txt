Feedfiller
==========

.. contents::

What is it?
===========

*Feedfiller* is intended to work alongside collective.feedfeeder, and fill
all the news feed items with the clean body content of the page they 
refer to.  If it does not 'know' the page format of the target page, all 
it can do is include the whole page. We will improve this as the 
project develops. 

Clearly there are potential copyright issues with the re-publishing of
copyrighted works. But for research and analysis purposes, these may not
be an issue for your organization. Our own purpose is to use collected 
text for classification and analysis for internal use. You should
seek your own legal advice on this topic.

How does it work?
=================

Feedfiller subscribes to the event created after storage of each news feed
item created by FeedFeeder and fetches the target page of that item. This
means that all items will be be filled with the content of the page they refer
to. Fetched pages are flayed ("Flay: Verb: to strip off the skin or surface
of") by a Flayer looked up in a FlayerRegistry by URL.

Flayers may be easily written to accomodate new pages. Flayers can be
created and registered for different sections of a site, in case HTML 
structure varies in sub-trees of the site. 

If no flayer is registered for the URL, a default flayer is used that
returns the whole body of the page.

Currently site-specific flayers try to reveal author, copyright, and body, 
but the default flayer  

The flayer base-class currently stores the original page fetched from 
the server, to facilitate further development and refinemement of flayers
without repeatedly fetching content.

TODO
====

The next step is to develop a table-driven flayer, for which table entries
can be generated interactively by clicking on an enhanced version of the 
default flay, a bit like a basic firebug view of the structure of a page
with buttons to manually select the body area of a page. This will
rmoyrequire a new view for this purpose, available to managers.

Eventually the table-drive flayer should be able to handle the complexity of 
the BBC news page.

CREDITS
=======

The project was started by Russ Ferriday, Topia Systems Ltd, in November, 2008.

Thanks to Zest Software and the van Rees brothers for FeedFeeder.

Contributions are welcome, and contributors are listed below:




  
  


