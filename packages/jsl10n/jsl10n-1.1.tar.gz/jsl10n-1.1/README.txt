Javascript localization for Zope / Plone
========================================
jsl10n.js provides a function called 'translate' which takes at least 3 arguments:
 - the i18n domain;
 - an array of objects with the properties 'msgid' and 'default' set to the translation ID and default value, appropriately;
 - a callback function, which will be called with a single object argument with properties mapping translation IDs to translated strings once they have been retrieved. Further to these, there are 2 optional arguments:
 - a boolean value which when set to 'true' will cause the translations to be retrieved with each page load;
 - a boolean value which when set to 'true' causes debugging messages to be printed to the Javascript console.
The function uses AJAX to call the view 'translate.js' which returns the JSON object given to the callback function. If the JSON call fails, the callback will still be triggered with the default values returned. Fallbacks should be implemented.

Example usage
-------------
required_translations = [
  {'msgid':'my_message',
   'default':'Hello world!'}
  ];
translate('domain', required_translations,
  function (translations) {
    alert(translations['my_message']);
  }
);

Caveats
-------
 - Any caching should use GET variables in the cache key for 'translate.js'.
 - These strings are not picked up by i18ndude, and therefore if they do not appear elsewhere in the codebase (in templates or Python code), they will not be added automatically to the POT files.
 - Since the POT files are managed automatically, if the strings are added to the POT files manually, they will be removed on next update. There are two possible solutions to this:
  1) Define a new domain which is managed manuall;
  2) Create a dummy template file somewhere in the codebase which is never actually called, but contains all the msgids and defaults used exclusively in Javascript;
  3) Include the translations in sections of relevant templates in sections which are never rendered, for example:

<tal:comment tal:replace="nothing">
  <span i18n:translate="my_message">Hello world!</span>
</tal:comment>

Dependencies
------------
simplejson_
.. _simplejson: http://pypi.python.org/pypi/simplejson/

Installation
============

Without buildout
----------------
Install this package in either your system path packages or in the lib/python
directory of your Zope instance. You can do this using either easy_install or
via the setup.py script. You'll also need to install plone.keyring in the same
fashion.

After installing the package it needs to be registered in your Zope instance.
This can be done by putting a jsl10n-configure.zcml file in the
etc/package-includes directory with this content::

  <include package="jsl10n" />

or, alternatively, you can add that line to the configure.zcml in a package or
Product that is already registered.

With buildout
-------------
eggs = jsl10n
zcml = jsl10n

Copyright
=========
Copyright 2010 Isotoma Limited

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
