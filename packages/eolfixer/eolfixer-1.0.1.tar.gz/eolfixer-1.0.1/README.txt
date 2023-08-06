EOL fixer script
================


What the script does
--------------------

The script goes through a directory structure and fixes non-native EOL endings
in non-binary files.  So the windows line endings are gone if you work on
linux (and probably vice versa, though I didn't try).

Numerous people forget to set native EOL line endings by default in their main
svn config file (see `zope's svn explanation
<http://www.zope.org/DevHome/Subversion/SubversionConfigurationForLineEndings>`_
why this is something you need to do).

The script sets the related svn property ``eol-style`` to native when not set
yet.


History and origin
------------------

Original script (and thus 99% of the functionality) is from Holger Krekel from
the `pypy project <http://codespeak.net/pypy/dist/pypy/doc/>`_.

A couple of years ago I got a script from Guido Wesdorp for cleaning up EOL
styles in svn.  I've long kept a private (modified) copy of that file and only
later found out that it was from the pypy project:
http://codespeak.net/pypy/dist/pypy/tool/fixeol .

Some changes to the original script:

- Couple of extra file extensions that are checked (like ``.zcml`` and
  ``.ini`` files and also ``_tmpl`` files like in paster skeletons).

- Some code cleanup and optimisation.

- Added a setup.py and a console_scripts entry point to make it
  easy_installable.
