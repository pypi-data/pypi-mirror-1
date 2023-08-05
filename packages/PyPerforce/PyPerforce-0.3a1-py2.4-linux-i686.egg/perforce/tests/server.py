"""perforce.tests.server - Utilities for starting a test Perforce server.

PerforceServerMixin - Class that can be inherited by TestCase classes to
  support starting a temporary 2-user licensed Perforce server with a new
  database for each test. 
"""

import os
import os.path
import tempfile
import subprocess
import platform

def _cygwinToWindowsPath(path):
  """Convert a unix-style cygwin path to a windows style path.

  @raise OSError: If the conversion failed for some reason.
  """
  proc = subprocess.Popen(['cygpath', '-w', path],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.wait() != 0:
    raise OSError(stderr)
  else:
    return stdout.strip()
  
class PerforceServerException(Exception):
  """Exception thrown when the Perforce server fails for some reason.
  """
  pass

class PerforceServerMixin(object):
  """A test case mixin that starts a Perforce server with a
  new temporary database that can be used for testing.
  """

  def __init__(self, port='1667', p4d='p4d', unicodeMode=False):
    self._p4dExecutable = p4d
    self._p4dProcess = None
    self._root = None
    self._log = None
    self._journal = None
    self._unicode = unicodeMode
    self.port = 'localhost:%i' % int(port)
    
  def setUp(self):
    assert self._p4dProcess is None
    
    self._root = tempfile.mkdtemp('', 'test-p4d')
    self._journal = os.path.join(self._root, 'journal')
    self._log = os.path.join(self._root, 'log')
    self._stdout = os.path.join(self._root, 'stdout')
    self._stderr = os.path.join(self._root, 'stderr')

    if platform.system().lower().startswith('cygwin'):
      # The cygwin platform uses the Windows native p4d executable which doesn't
      # understand unix-style cygwin paths.
      # Convert them to windows-style paths before starting the server.
      args = [self._p4dExecutable,
              '-r', _cygwinToWindowsPath(self._root),
              '-J', _cygwinToWindowsPath(self._journal),
              '-L', _cygwinToWindowsPath(self._log),
              '-p', self.port,
              ]
    else:
      args = [self._p4dExecutable,
              '-r', self._root,
              '-J', self._journal,
              '-L', self._log,
              '-p', self.port,
              ]
            
    if self._unicode:
      # Create the Perforce database in unicode mode
      p = subprocess.Popen(args=args + ['-xi'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
      out, err = p.communicate()
      if p.wait() != 0:
        raise PerforceServerException(out)
    
    self._p4dProcess = subprocess.Popen(args=args,
                                        stdout=file(self._stdout, 'wb'),
                                        stderr=file(self._stderr, 'wb'))

    # Wait for the server to start accepting connections before returning                             
    try:
      self._waitForServerUp()
    except PerforceServerException:
      try:
        self.tearDown()
      except PerforceServerException:
        pass
      raise
  
  def _waitForServerUp(self, howLong=3.0):
    """Wait for the Perforce server to come up and start accepting connections."""
    
    from perforce import Connection, ConnectionFailed, CharSet
    c = Connection()
    c.port = self.port
    if self._unicode:
      c.charset = CharSet.UTF_8
    else:
      c.charset = CharSet.NOCONV
    
    retryDelay = 0.5
    retryCount = int(howLong / retryDelay)
    for i in xrange(retryCount):
      try:
        c.connect()
        c.disconnect()
        break
      except ConnectionFailed:
        import time
        time.sleep(retryDelay)
    else:
      raise PerforceServerException('p4d failed to start in a timely manner')
  
  def _terminateCleanly(self):
    # Try to terminate the Perforce server cleanly using 'p4 admin stop'
    from perforce import Connection, ConnectionFailed, CharSet
    c = Connection()
    c.port = self.port
    if self._unicode:
      c.charset = CharSet.UTF_8
    else:
      c.charset = CharSet.NOCONV
    try:
      c.connect()
      try:
        results = c.run('admin', 'stop')
        if results.errors:
          err = '\n'.join((str(e) for e in results.errors))
          raise PerforceServerException(
            'Failed to stop Perforce server:\n%s' % err) 
      finally:
        c.disconnect()
    except ConnectionFailed, e:
      raise PerforceServerException(
        'Failed to stop Perforce server: connection failed')
    
    if self._p4dProcess.wait() != 0:
      raise PerforceServerException(
        'Perforce server terminated with an error')

  def _terminateForcibly(self):
    assert self._p4dProcess is not None
    if hasattr(os, 'kill'):
      import signal
      os.kill(self._p4dProcess.pid, signal.SIGTERM)
    else:
      try:
        import win32api
        win32api.TerminateProcess(int(self._p4dProcess._handle), -1)
      except ImportError:
        try:
          import ctypes
          ctypes.windll.kernel32.TerminateProcess(
            int(self._p4dProcess._handle), -1)
        except ImportError:
          raise OSError("Don't know how to terminate P4D process")
        
    self._p4dProcess.wait()
    
  def _terminateServer(self):
    assert self._p4dProcess is not None
    try:
      try:
        self._terminateCleanly()
      except:
        self._terminateForcibly()
    finally:
      self._p4dProcess = None
    
  def _cleanupDatabase(self):
    try:
      for root, dirs, files in os.walk(self._root, topdown=False):
        for name in files:
          os.remove(os.path.join(root, name))
        for name in dirs:
          os.rmdir(os.path.join(root, name))
      os.rmdir(self._root)
    finally:
      self._root = None
      self._log = None
      self._journal = None
      self._stdout = None
      self._stderr = None
    
  def tearDown(self):
    self._terminateServer()
    self._cleanupDatabase()
