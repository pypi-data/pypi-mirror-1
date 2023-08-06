urllibcache
===========

This is a simple caching handler for urllib2.

Usage
-----

Either use the build_opener function which takes the path to the cache folder
and returns an OpenerDirector instance. You can then use it's open method to
open urls normally. If the file was already downloaded, then it will be taken
from the cache.

You can also use the CachedHandler wherever it's useful within urllib2. This
also takes the path to cache folder as an argument of the constructor.

Be aware that the caching is very simple. It detects incomplete downloads but
doesn't take any caching headers into account. To invalidate the cache you
have to delete the files in the cache folder.

Changelog
---------

1.0.1 - 2008-07-23
------------------

* Fixed packaging.
  [fschulze]

1.0 - 2008-07-22
----------------

* Initial release.
  [fschulze]
