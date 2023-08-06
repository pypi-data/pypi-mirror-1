Introduction
============

Store single lists as an int rather than IISet, which speeds up access and reduces the number of objects loaded/stored in ZODB.  You will need to clear and rebuild the DateRangeIndexes for it to take effect.
