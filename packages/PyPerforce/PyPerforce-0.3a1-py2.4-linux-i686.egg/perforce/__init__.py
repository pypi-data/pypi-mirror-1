"""A Python interface for the Perforce SCM

Sub Modules
===========

  L{perforce.api}
  ---------------
    Wrappers directly onto Perforce's C++ API.

  L{perforce.async}
  -----------------
    Asynchronous interface to the Perforce Python API using Twisted.

  L{perforce.connection}
  ----------------------
    Defines the Connection class for connecting to a Perforce server and
    running commands on the connection.

  L{perforce.forms}
  -----------------
    Module containing Perforce form related classes.

  L{perforce.results}
  -------------------
    Module containing helper classes for processing output of Perforce
    commands.

  L{perforce.objects}
  -------------------
    Module containing object oriented interfaces for Perforce entities
    such as branches, users, clients etc.
    
  L{perforce.tests}
  -----------------
    Unit tests for the Perforce Python API.
"""

__version__   = '0.3'
__author__    = 'Lewis Baker'
__email__     = 'lewisbaker@users.sourceforge.net'
__copyright__ = '(c) 2005-2006 Maptek Pty. Ltd.'

__all__ = ['api', 'async', 'connection', 'forms', 'objects', 'results',
           'CharSet', 'Message', 'PerforceError',
           'Connection', 'ConnectionFailed', 'ConnectionDropped',
           'Branch', 'Client', 'Label', 'User', 'Change', 'CommandError']

from perforce.api import CharSet, Error as Message, PerforceError
from perforce.connection import Connection, ConnectionFailed, ConnectionDropped
from perforce.objects import Branch, Client, Label, User, Change, Counter, \
  CommandError
