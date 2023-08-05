DoDoStorage is meant as a User-Space write-once Filesystem. Much Inspiration
is drawn from MoglieFS http://www.danga.com/mogilefs/ - but DoDoStorage it is
much simpler.

With DoDoStorage you can store files - "Documents" in DoDoStorage speak. For
each file you get an opaque "Document key" to retrive it. Stored Files are
immutable - you can't change or delete them. Every Document has an
"category" whichs help to destinguish classes of Documents, a mime-type and
a timestamp. It also has a set of arbitrary attributes.

DoDoStorage is meant to be accessed via an RESTful HTTP API.

Please see dodostorage/__init__.py and dodostorage/dodoserver for further
enlightenment.

http://blogs.23.nu/c0re/stories/15297/ and the entries linked from there have 
some further background.
