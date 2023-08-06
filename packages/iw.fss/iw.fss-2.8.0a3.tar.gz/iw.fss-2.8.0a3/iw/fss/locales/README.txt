##################
Translating iw.fss
##################

Requirements
############

What you need:

* Unix based development environment (need help for Windows
  support). Maybe this works with Windows/Cygwin, maybe not (feedback
  and help needed).

* `msgfmt` utility.

* `i18ndude <http://plone.org/products/i18ndude>`_

* Read `this
  <http://maurits.vanrees.org/weblog/archive/2007/09/i18n-locales-and-plone-3.0>`_
  for some enlightenments if you're somehow a newbie in Zope 3 style
  translations.

Operations
##########

Rebuilding iwfss.pot
====================

This may be required if you added, changed, removed translation keys
somewhere in the Python or page templates of iw.fss::

  $ cd locales
  $ sh rebuild_pot.sh

Synching various .po files with changes in iw.fss.pot
=====================================================

If changes have occcured in `iw.fss.pot`, you must apply these changes
to the various .po files (and kick their respective translators)::

  $ cd locales
  $ sh sync_pos.sh

Compile all .po files
=====================

If you made changes in one or more .po file, Zope needs the binary
version of your translations::

  $ cd locales
  $ sh make_mos.sh

Add your translation
====================

Say you want to translate FSS to the `xx`language.

  $ cd locales
  $ mkdir -p xx/LC_MESSAGES
  $ touch xx/LC_MESSAGES/iw.fss.po
  $ sh sync_pos.sh
  $ vi xx/LC_MESSAGES/iw.fss.po # Add your translations
  $ sh make_mos.sh
  $ svn add xx
  $ svn ci -m "Added translation for martian"
  $ vi README.txt # Add yourself in the "Credits" chapter below

Issues
######

Since `iw.fss` is a Zope 3 style component and not a Zope 2 product,
we can't provide the additional translation for the `plone` domain.

To work around this, you need to add this line in any .po file for the
Plone domain in any of your products::

  msgid "FileSystem storage Preferences"
  msgstr "<Your translation here...>"


Credits
#######

* English (en) and French (fr): `Ingeniweb team <support@ingeniweb.com>`_
* Czeck (cs) translation: `Radim Novotny <novotny.radim@gmail.com>`_
* Brazilian Portuguese (pt_BR) translation: `Érico Andrei <erico@simplesconsultoria.com.br>`_
* Basque (eu) and Spanish (es): `Mikel Larreategi - CodeSyntax <mlarreategi@codesyntax.com>`_

