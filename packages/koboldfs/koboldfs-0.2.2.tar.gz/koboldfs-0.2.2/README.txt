KoboldFS
========

KoboldFS is an application-level distributed file system written in Python.
Inspired by MogileFS[1], it shares some of its properties and features:

 * Application level -- no special kernel modules required;

 * No single point of failure -- all the components of a KoboldFS setup
   (servers and database) can be run on multiple machines, so there's no single
   point of failure (a minimum of 2 machines is recommended);

 * Automatic file replication -- files are automatically replicated between all
   the servers. In KoboldFS there is no concept of "class", so it is not
   possible to specify if a given file has to be replicated only in a subset of
   the available servers;

 * "Better than RAID" -- in a non-SAN RAID setup, the disks are redundant, but
   the host isn't. If you lose the entire machine, the files are inaccessible.
   KoboldFS replicates the files between devices which are on different hosts,
   so files are always available;

 * Flat name space -- Files are identified by named keys in a flat, global
   name space. You can create as many name spaces as you'd like, so multiple
   applications with potentially conflicting keys can run on the same MogileFS
   installation;

 * Shared-Nothing -- KoboldFS doesn't depend on a pricey SAN with shared disks.
   Every machine maintains its own local disks;

 * No RAID required -- Local disks on KoboldFS storage nodes can be in a RAID,
   or not. It's cheaper not to, as RAID doesn't buy you any safety that
   MogileFS doesn't already provide;

 * Local file system agnostic -- Local disks on KoboldFS storage nodes can be
   formatted with your file system of choice (ext3, XFS, etc..). KoboldFS does
   its own internal directory hashing so it doesn't hit file system limits such
   as "max files per directory" or "max directories per directory". Use what
   you're comfortable with;

 * Completely portable -- it is a python-only module, thus can be run on any
   operating system and architecture which is supported by Python;

 * Database-agnostic -- it can run with any SQL database; actually only the
   PostgreSQL support is implemented, but adding support for new databases is
   quick and easy;

 * Support for serving the stored files directly by an external web server,
   reducing the load on the application servers.

KoboldFS is not:
----------------

 * POSIX Compliant -- you don't run regular Unix applications or databases
   against KoboldFS; it's meant for archiving write-once files and doing only
   sequential reads (though you can modify a file by way of overwriting it with
   a new version).

Sample usage:
-------------

    >>> from StringIO import StringIO
    >>> from koboldfs import Client

    >>> client = Client('demo', servers=['127.0.0.1:9876', '127.0.0.1:9875'])

    >>> print client.ping()
    True

    >>> print client.put('motd', '/etc/motd')
    True

    >>> output = StringIO()
    >>> if client.get('motd', output):
    >>>    output.seek(0)
    >>>    print output.read()
    Linux...

    >>> print client.get_url('motd')
    http://...

    >>> print client.delete('motd')
    True

    >>> client.get('motd', output)
    False

    >>> assert client.get_url('motd') is None
    True

References:
-----------

    1. http://www.danga.com/mogilefs
