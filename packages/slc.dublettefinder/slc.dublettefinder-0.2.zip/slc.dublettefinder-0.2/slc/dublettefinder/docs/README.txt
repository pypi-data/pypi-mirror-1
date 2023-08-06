SYSLAB DUBLETTEFINDER:

The goal of slc.dublettefinder is to find duplicate files (dublettes) in the
ZODB and warn the user via a validation error.

The user is given the options to ignore the validation error and continue.

There is also a portlet that will appear when the context is a correctly
adapted archetype that contains file fields. The portlet will display the titles
and URLs of objects that contain files that are possible duplications of the
files contained in the schema of the current context.

Lastly there is a browser page method @@findDuplicateFiles, that will return a
zipped csv file containing all the possible file duplications in a site.

HOW TO USE:

Archetype objects that contain fileFields can be adapted by two adapters in
extensions/file.py to enable validation that checks for similar files according
to either file size or the file's name, depending on the specific adapter.

The objects are adapted via zcml. Check out extensions/configure.zcml

When a user creates a object that is adapted (like ATFile) and uploads a file
that already exists in the Site, a validation error will appear that alerts the
users of the possible duplicates in the site.

HOW TO INSTALL:

slc.dublettefinder is in the form of a python egg. Install it as you would any 
eggified Plone product.

CONTACT:
Author: JC Brand
Email: brand@syslab.com, jc@opkode.com



