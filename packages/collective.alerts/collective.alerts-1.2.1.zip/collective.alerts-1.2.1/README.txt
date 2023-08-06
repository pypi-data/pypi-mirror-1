Introduction
============

This product implements Cory LaViska's 'JQuery Alert Dialogs' for Plone.

Basically, they are fancy, styleable replacements for the standard
'alert', 'confirm' and 'prompt' browser functions.

Please see: http://abeautifulsite.net/notebook/87 for more information.


Usage
-----

When collective.alerts is installed and the jquery.alerts library registered in
portal_javascripts (should be automatic), then the alerts can be called as
follows:

 - jAlert( message, [title, callback] )
 - jConfirm( message, [title, callback] )
 - jPrompt( message, [value, title, callback] )


