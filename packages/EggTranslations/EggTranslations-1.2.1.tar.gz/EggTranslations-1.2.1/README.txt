========================
EggTranslations Overview
========================

EggTranslations is a flexible object-oriented resource
loader that is designed to work in projects that are
distributed as `Python eggs`_. Its main goals are to
support localization of resources (e.g. images, help
files and other documentation), and to allow localization
of text in your application by loading `GNU gettext`_
``.mo`` files. However, you don't have to be dealing with
localizable resources to use EggTranslations: You can
use it to organize non-localizable resources, too.

.. _Python eggs: http://peak.telecommunity.com/DevCenter/PythonEggs
.. _GNU gettext: http://www.gnu.org/software/gettext/

.. contents::

Source and Installation
=======================
The (read-only) subversion trunk is available at:

    `http://svn.osafoundation.org/eggtranslations/trunk`_

.. _http://svn.osafoundation.org/eggtranslations/trunk: http://svn.osafoundation.org/eggtranslations/trunk#egg=eggtranslations-dev


EggTranslations is shipped as an `easy_install`_-able source
package. So, you can install it directly, or list it as a
dependency if you're using setuptools_.

How it works
============

The big idea here is that you can have a project or application
that you ship as a python egg, but whose localized resources
live in entirely separate python eggs. So, you can ship your
project's translations separately, so long as you package
resources as outlined below, and use EggTranslation APIs
to look up these resources.

EggTranslations works by combining the following:

   * A set of eggs, each containing a **configuration file**,
     called ``resources.ini`` by default. This file is located
     in each egg's ``.egg-info`` directory.

   * **Resource files**, also contained in the ``.egg-info``
     directory.

   * A **translations** object (an instance of ``EggTranslations``
     or a subclass thereof). Each EggTranslations instance can
     customize the locale set it supports, the name of the
     configuration file to parse, and whether to employ locale set
     fallback_ for localization and resource look up.

Let's look at each of these in turn:

The configuration (``resources.ini``) file
------------------------------------------

This file is in `INI file format`_, as parsed by the
`configobj`_ parser. This means it consists of *parameters*
(key-value pairs), divided into *sections*.

Sections
~~~~~~~~
Here's an example (empty) section::

    [MyGreatProject::en]

The string before the ``::`` identifies the project you're
specifying resources for. (You'll later pass this project
name into various ``EggTranslation`` methods to read or
retrieve resources from the egg).

The string after the ``::`` specifies which locales this
section applies to. In general, you can supply a comma-separated
list of locales, e.g.::

    [MyGreatProject::es, es_UY]

would specify that these resources apply to both Spanish (``es``) and
Uruguyan Spanish (``es_UY``). The localizations of ``MyGreatProject``
can be shipped in different Python eggs.

The ``all`` locale
~~~~~~~~~~~~~~~~~~
The string ``all`` as a locale name is special: It is used
to specify that the parameters that follow can be used as a
fallback_ (i.e. are used if no other value is found). Another
way of looking at this is that you can use ``all`` to specify
where to find non-localized resources.

Parameters
~~~~~~~~~~
Each key-value pair you specify in a section can be one of:

    1. A translated **string value**, e.g. ::
    
        status_message = Unable to load file.

    2. A **path** relative to your egg's ``.egg-info`` directory::
    
        help_files = resources/help

We'll examine how to use these in code below, but for now
let's note that there are several uses for the 2nd case here:
You can point at an entire directory of resources or at individual
resource files. In particular, you can also specify a gettext
``.mo`` (binary message object file), which will contain
translations for a particular locale.

Resource files
--------------
As mentioned before, all resource files are stored within
directories beneath ``.egg-info``. Note that since we are
`accessing resources`_ using the ``pkg_resources`` API, all
paths should be specified in your config file using '/' as
path separator, not an OS-dependent path separator.

While the most common cases of localizable files are
documentation and string translations, it's not uncommon
to allow localization of image resources, too (the most
infamous example is the octagonal "stop sign" icon, which
doesn't make sense in all locales).

Translation objects: The ``EggTranslations`` class
--------------------------------------------------

The ``EggTranslations`` constructor takes no arguments::

  >>> from egg_translations import *
  >>> translation = EggTranslations()

There is a separate initialization step where
you pass in the locale set you're interested in::

  >>> translation.initialize(['fr_CA', 'fr'])

The reason for this is that frequently you'll set up
your object as a global, but will want to read the
user's preferred set of locales from the operating
system (e.g. from a 3rd-party library such as
`PyICU`_) or from some kind of preference persistent
settings.

.. _fallback:

``EggTranslations.initialize`` also takes a Boolean
``fallback`` keyword argument, which defaults to ``True``.
If you set it to ``False`` you will disable finding
resources in the ``all`` pseudo-locale, unless you
explicitly pass in ``"all"`` to the various resources
lookup/retrieval APIs.

``EggTranslations`` supports several methods for retrieving
resources. For example, if your ``resources.ini`` file contained
an entry::

    [MyProject::all]
    readme = docs/README.txt

you could get the contents of ``README.txt`` as a unicode string [#]_ via::

    translation.getResourceAsString("MyProject", "readme")

This would allow localizers to translate ``README.txt``, so long
as they shipped it in an egg with a suitable ``resources.ini``. The
simplest way to do this is to have the translation egg match
the filesystem layout of MyProject's egg::

    [MyProject:es]
    readme = docs/README.txt

There's no particular requirement to do this, so long as the config
file entry points at a valid file. In other words, the Spanish
translation egg could have an entry::

    [MyProject:es]
    readme = docs/es/LEER

and the code using ``getResourceAsString()`` above would work
in either locale, so long as the file ``LEER`` was located
in ``docs/es`` beneath the ``.egg-info`` directory.

Depending on what type of resource you have, there are various
``EggTranslations`` methods that will help to discover or
extract resources. Besides the above, there's also a ``getText``
method that can be used to look up a string's translation in a
``.mo`` file.

For more details on accessing the contents of resource files, see
the `full documentation` for the ``EggTranslations`` class.

.. [#] All ``EggTranslations`` methods returning a ``unicode`` default
   to assuming UTF-8 encoding, but can be overridden using the
   ``encoding`` keyword argument.

More on Locales
===============
EggTranslations assumes that a locale is an ASCII string
consisting of a two-letter language code, optionally followed
by an underscore and a two-letter country code, like ``"en"``
or ``"zh_TW"``. It will attempt to canonicalize locales
(i.e. truncate them if longer, and/or correct the case
of the country and language codes).

Some libraries (e.g. ICU) use locale names using a slightly
different format. If you want to use these, you should
subclass ``EggTranslations`` and override the
``normalizeLocale()``, ``isValidLocaleForm()`` and
``stripEncodingCode()`` methods.

Putting it all Together
=======================
A common arrangement is to ship an application containing
fallback ("``all``") resources in its ``.egg-info``, and
then ship its localizations as plugin eggs. For example,
this is how Chandler_ packages its various translation
files.

Since ``EggTranslations`` `listens for egg activations`_,
this allows the application to detect new translations
automatically, so long as the ``EggTranslations`` instance
has been ``initialize()``-ed before the translation
plugins have been loaded.

Feedback
========
Feedback, comments or questions are welcome, either via
the `chandler-dev mailing list`_, or on IRC_.
 
Example configuration file
==========================

For reference, here is an example resource.ini file::

  # This is an example comment in a resource
  # ini file
  
  [myEggProject::all]
  welcome.message=Greetings from my egg #This is the default message my
                                        #users will see.
  
  default.image = resource/default.png  #This is the default image my
                                        #users will see.
  default.directory = resource
  
  [myEggProject::fr_CA, fr_FR, fr] #All of these locales will
                                   #use the entries defined below
  welcome.message = Bonjour
  default.image = locale/fr/resources/default.png
  
  ###
  # This gettext catalog
  # will automatically get
  # loaded if the EggTranslations
  # locale set contains one or more or the
  # following 'fr_CA', 'fr_FR', 'fr'
  ###
  
  gettext.catalog = locale/fr/myproject.mo
  default.directory locale/fr/resources
  
  [myEggProject::es_UY, es]
  welcome.message = Hola
  default.image = locale/es/resources/default.png
  
  ###
  # This gettext catalog will automatically get
  # loaded if the EggTranslations
  # locale set contains one or more or the
  # following 'es_UY', 'es'
  ###
  
  gettext.catalog = locale/es/myproject.mo
  
  default.directory = locale/es/resources
  
  [yourEggProject::fr]
  getext.catalog=locale/fr/yourproject.mo

.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _INI file format: http://en.wikipedia.org/wiki/INI_file
.. _configobj: http://www.voidspace.org.uk/python/configobj.html
.. _PyICU: http://pyicu.osafoundation.org/
.. _accessing resources: http://peak.telecommunity.com/DevCenter/PythonEggs#accessing-package-resources
.. _listens for egg activations: http://peak.telecommunity.com/DevCenter/PkgResources#receiving-change-notifications
.. _full documentation: http://packages.python.org/EggTranslations/
.. _Chandler: http://chandlerproject.org/
.. _chandler-dev mailing list: http://chandlerproject.org/mailinglists#ChandlerDevelopment
.. _IRC: http://chandlerproject.org/irc

Changelog
=========

1.2.1 (2009/06/26)
------------------
* Fix some SyntaxWarnings in Python 2.6, which arose from incorrect use of
  the assert statement.
  [grant]

1.2 (2009/02/11)
----------------

* Cleaned up project and docs for Cheeseshop upload.
  [grant]

* Added API for locale normalization, which allows subclasses to implement,
  say, ICU locale names like "zh_Hans".
  [grant]

1.1 (2007/10/15)
----------------

* Added the ability to discover what locales are available for a particular
  project. This info is very handy and can map directly to a UI locale picker
  widget.
  [bkirsch]

* Expanded the exception handling of hasTranslation.
  [bkirsch]

1.0 (2007/04/25)
----------------
* Moved the version to 1.0 since the package has been in use for 6 months
  in Chandler with no bugs reported.
  [bkirsch]

* Add the hasTranslation method which checks if a gettext .mo file exists
  and is loaded for the given locale
  [bkirsch]

<1.0
----
* Created separate project from http://svn.osafoundation.org/chandler/trunk/chandler/projects/EggTranslations-plugin (rev 13152)
  [bear]
