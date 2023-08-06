eCards
======
eCards is a simple Plone-product that allows your website visitors to
send eCards to people via email. eCards can help boost website
traffic and visitor engagement.

Product home is http://plone.org/products/ecards. 
A `documentation area`_ and `issue tracker`_ are available at the linked locations.

.. _documentation area: http://plone.org/products/ecards/documentation
.. _issue tracker: http://plone.org/products/ecards/issues

Please use the Plone users' mailing list or the #plone irc channel for
support requests. If you are unable to get your questions answered
there, or are interested in helping develop the product, see CREDITS.txt 
within the same directory.

Compatibility
***************

* Plone 3.x-series, if you need to use eCards with version 2.5.x, see
http://plone.org/products/ecards/releases/1.0

Overview
***************

For site managers:

* Addition of new content type "eCard Collection" which can contain selected eCards
* "eCard" content type that contains the image and an option thumbnail for overriding 
  the default generated thumbnail
* Configuration of layout of eCard Collection view, to suit variable site design widths
  (i.e. choose the number of eCards in a row, which will not overextend the main content area)
* Configuration of a "pull" message appended to the end of each email that raises awareness about 
  the organization hosting the eCard application where the eCard was sent.

For site users:

* User can choose amongst multiple eCards from a thumbnail gallery, as uploaded by the site managers
* Users can add a personalized message to their eCards.
* Cards are emailed to recipients.

Fully customizable templates

* ecardcollection_view - a page that includes HTML content, a 
  thumbnail gallery of eCards, and email settings.
* ecardpopup_view - loaded when an eCard is chosen from the collection view, includes the full sized eCard image,
  a byline for the image, and HTML email message to be appended (see above), the form fields required for the user
  to send the email.
* email_template - contains the HTML-rich email template that gets sent out to include the
  chosen eCard and custom message.  Note: we're passing several variables via options dictionary.  If you want to include
  additional "dynamic" data in your email template, you'll need to customize ecardsuccess.cpy as well.

You can customize these templates via the ZMI or on the filesystem to match your site's branding.

Installation & Setup
**********************

See INSTALL.txt

Demo
***************

You can see customized eCard implementations in action at:

* `SnowLeopard.org`_
* `The Women's Field Guide`_

.. _SnowLeopard.org: http://www.snowleopard.org/photos/ecard
.. _The Women's Field Guide: http://www.womansfieldguide.com/
