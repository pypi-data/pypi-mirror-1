plone.recipe.distros
====================

Options
-------

urls
    The URLs of the archives to download. The archives specified in the same
    part will be extracted into the same parts folder named after the part.
    The full path to that folder will be available as 'location' from the
    parts option dictionary.

nested-packages
    The file names of one or more of the archives in the urls list.
    This will cause only the Python packages (identified by a __init__.py) in
    the top folder in the archive to be extracted into the destination.

version-suffix-packages
    The file names of one or more of the archives in the urls list.
    This will cause the part after the last dash to be omitted from the created
    destination folder.

Reporting bugs or asking questions
----------------------------------

We have a shared bugtracker and help desk on Launchpad:
https://bugs.launchpad.net/collective.buildout/
