"""perforce.async - Asynchronous Perforce Python API using Twisted

Sub Modules
===========

 - L{connection}
   Defines a connection object that uses Twisted deferreds to handle
   asynchronous callbacks on Perforce events.
 - L{objects}
   A collection of object-oriented interfaces for accessing Perforce entities
   similar to the L{perforce.objects} module, only using Twisted deferreds
   to provide asynchronous access.
"""

__all__ = ['connection', 'objects']
