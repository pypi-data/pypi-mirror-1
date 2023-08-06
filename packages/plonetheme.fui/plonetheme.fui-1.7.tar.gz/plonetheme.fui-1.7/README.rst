README
======

Plone theme written for *Fagutvalget ved Institutt for informatikk*
(http://fui.ifi.uio.no).

The only file I have modified, except some minor adjustments to ``setup.py``, is
``plonetheme/fui/browser/stylesheets/main.css``. I have simply inspected the
xhtml source produced by plone, and made the CSS by the trial and error method.




Release a new version
=====================

Release a new version to pypi.python.org with::

    ~$ python setup.py egg_info -RDb "" sdist upload
