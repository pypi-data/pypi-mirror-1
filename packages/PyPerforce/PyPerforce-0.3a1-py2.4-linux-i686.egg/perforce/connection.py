"""Perforce connection abstractions.

L{Connection} - Manages a single connection to a Perforce server.
"""

__all__ = ['Connection', 'ConnectionFailed', 'ConnectionDropped']

import perforce.api
from perforce.api import ConnectionFailed, ConnectionDropped

# Helper for declaring instance properties
def attribute(func):
    return property(*func())

class Connection(object):
    """A single connection to a Perforce server.

    Use instances of this class to connect to a Perforce server and run
    Perforce commands on the server.

    Example::
      | c = Connection()
      | c.port = 'my-server:1666'
      | try:
      |   c.connect()
      |   c.client = 'my-client'
      |   results = c.run('sync')
      |   c.disconnect()
      |   for msg in results.messages:
      |     print str(msg)
      | except ConnectionFailed:
      |   print 'Could not connect to Perforce server.'
      | except ConnectionDropped:
      |   print 'Connection to Perforce server dropped.'
    """
    
    __slots__ = ['_client', '_connected']

    def __init__(self, **options):
        """Construct a new Perforce connection object.
        
        The connection is initially disconnected.

        @param options: Connection attributes to set on construction.

        @keyword port: See L{self.port}
        @keyword user: See L{self.user}
        @keyword password: See L{self.password}
        @keyword client: See L{self.client}
        @keyword host: See L{self.host}
        @keyword language: See L{self.language}
        @keyword charset: See L{self.charset}
        @keyword cwd: See L{self.cwd}
        @keyword api: See L{self.api}
        @keyword ticketFile: See L{self.ticketFile}

        @see: L{connect}, L{connected}
        """
        self._client = perforce.api.ClientApi()
        self._connected = False

        # Set charset first as setting it can affect how the cwd
        # value is interpreted.
        if 'charset' in options:
            self.charset = options['charset']

        # Set cwd next as setting it can look for a P4CONFIG
        # file which can override the other settings.
        if 'cwd' in options:
            previousCharset = self.charset
            self.cwd = options['cwd']
            if self.charset != previousCharset:
                # Reset the charset to force a call to setTrans()
                self.charset = self.charset

        # Set the remaining overridables
        for opt in options:
            if opt not in ['cwd', 'charset']:
                setattr(self, opt, options[opt])

    def __del__(self):
        """Destruct the Perforce connection object.
        
        Disconnects from the Perforce server if still connected.
        
        @see: L{disconnect}
        """
        if self._connected:
            self._client.final()

    @attribute
    def connected():
        doc="""Flag indicating whether the Connection object is 
        currently connected to a Perforce server.

        @type: C{boolean}
            
        @see: L{connect}, L{disconnect}
        """
        def fget(self):
            return self._connected
        return (fget, None, None, doc)

    @attribute
    def api():
        doc="""The Perforce client protocol version used by the connection.

        Typical values:
          - C{'58'} for 2005.2
          - C{'57'} for 2004.1, 2004.2, 2005.1
          - C{'56'} for 2003.2
          - C{'55'} for 2003.1

        Example::
          | c.api = '56'   # Limit to Perforce 2003.2 behaviour
          | c.connect()

        @type: C{str}

        @note: Must be set prior to calling C{self.connect()} to have an
        effect on the connection's protocol version.

        @see: L{server}, L{connect}
        """
        def fset(self, value):
            self._client.setProtocol("api", value)
        return (None, fset, None, doc)

    @attribute
    def server():
        doc="""The Perforce server protocol version used by the connection.

        Possible values:
          - C{'20'} for 2005.2
          - C{'19'} for 2005.1
          - C{'18'} for 2004.2
          - C{'17'} for 2003.2
          - C{'16'} for 2003.1
          - C{'15'} for 2002.2
          - C{'13'} for 2002.1
          - C{'11'} for 2001.1
          - C{'10'} for 2000.2
          - C{'9'} for 2000.1
          - C{'0'} if server version not initialised, call L{run}.

        @type: C{str}

        @note: Is only initialised after running a command on this connection.

        @see: L{api}, L{run}
        """
        def fget(self):
            return self._client.getProtocol("server2")
        return (fget, None, None, doc)

    @attribute
    def nocase():
        doc="""Flag indicating whether the server is case insensitive.

        @note: Can only be queried after running a command on this connection.

        @type: C{boolean}

        @see: L{server}, L{run}
        """
        def fget(self):
            if self._client.getProtocol("nocase"):
                return True
            else:
                return False
        return (fget, None, None, doc)
    
    @attribute
    def charset():
        doc="""The character set to use for encoding unicode file data.

        Defaults to the value found in the P4CONFIG file if one exists,
        otherwise to the value of the P4CHARSET environment variable if set,
        otherwise to the value stored in the registry, otherwise to ''.

        Set this attribute to something other than C{'none'} to enable
        I{'unicode'} mode and allow connections to Unicode-enabled
        Perforce servers.

        Supported character sets:
          - C{'none'}
          - C{'utf8'}
          - C{'utf8-bom'} *
          - C{'iso8859-1'}
          - C{'iso8859-5'} *
          - C{'iso8859-15'}
          - C{'utf16'}
          - C{'utf16-nobom'} *
          - C{'utf16le'} *
          - C{'utf16be'} *
          - C{'utf16le-bom'} *
          - C{'utf16be-bom'} *
          - C{'shiftjis'}
          - C{'eucjp'}
          - C{'winansi'}
          - C{'winoem'}
          - C{'macosroman'}
          - C{'cp1251'} *
          - C{'koi8-r'} *

        * - Only available for Perforce 2005.2 or later clients
          
        @type: C{str} (may be set with L{perforce.CharSet} or C{NoneType})
        """
        def fget(self):
            return self._client.getCharset()
        def fset(self, value):
            if isinstance(value, perforce.api.CharSet):
                cs = value
                self._client.setCharset(str(value))
            else:
                cs = perforce.api.CharSet(value)
                self._client.setCharset(value)

            if cs.codec and cs.codec.lower().startswith('utf_16'):
                # UTF-16 can only be used for file content, use UTF-8 for
                # other character encodings.
                utf8 = perforce.api.CharSet.UTF_8
                self._client.setTrans(utf8, cs, utf8, utf8)
            else:
                self._client.setTrans(cs, cs, cs, cs)
            
        return (fget, fset, None, doc)

    @attribute
    def client():
        doc="""The Perforce client to use for subsequent commands.

        Defaults to the value in the P4CONFIG file if one exists, otherwise
        to the value of the P4CLIENT environment variable if set, otherwise
        to the value stored in the registry, otherwise to the machine name.

        @type: C{str} or C{unicode}
        """
        def fget(self):
            return self._client.getClient()
        def fset(self, value):
            self._client.setClient(value)
        return (fget, fset, None, doc)

    @attribute
    def config():
        doc="""The config file currently being used by this connection.

        The config file name is obtained from the P4CONFIG environment
        variable if set, otherwise from the value stored in the registry.
        The current working directory, L{cwd}, and its ancestors are
        searched for a config file. If a config file is found then it its
        path is returned, otherwise C{None} is returned.

        @note: Only available in Perforce 2005.2 or later clients.

        @type: C{str} or C{NoneType}
        """
        def fget(self):
            path = self._client.getConfig()
            if path == "noconfig":
                return None
            else:
                return path
        return (fget, None, None, doc)
    
    if float(perforce.api.version) < 2005.2:
        del config

    @attribute
    def cwd():
        doc="""The working directory to use for subsequent commands.

        This path is used to resolve relative local file system paths provided
        to Perforce commands to absolute paths.

        Defaults to the current working directory of the current process.

        @type: C{str} or C{unicode}

        @note: Setting the working directory for the L{Connection} causes
        Perforce to search for a new P4CONFIG file which, if found, may
        reset existing environment values.

        @see: L{config}
        """
        def fget(self):
            return self._client.getCwd()
        def fset(self, value):

            # Changing the cwd can cause a change in the charset
            previousCharset = self.charset
            
            self._client.setCwd(value)

            if self.charset != previousCharset:
                # Reset the charset to force a call to setTrans()
                self.charset = self.charset

        return (fget, fset, None, doc)

    @attribute
    def host():
        doc="""The hostname to identify as to the Perforce server.

        Defaults to the value in the P4CONFIG file if found, otherwise to the
        value of the P4HOST environment value, otherwise to the value in the
        registry, otherwise to the local machine name.

        @type: C{str} (may be set using C{unicode})
        """
        def fget(self):
            return self._client.getHost()
        def fset(self, value):
            self._client.setHost(value)
        return (fget, fset, None, doc)

    @attribute
    def language():
        doc="""The language to display Perforce messages in.

        Defaults to the value in the P4CONFIG file if found, otherwise to the
        value of the P4LANGUAGE environment value, otherwise to the value in
        the registry, otherwise to ''.

        @note: The Perforce server must have the particular language pack
        installed to support translated messages.

        @type: C{str} or C{unicode}
        """
        def fget(self):
            return self._client.getLanguage()
        def fset(self, value):
            self._client.setLanguage(value)
        return (fget, fset, None, doc)

    @attribute
    def os():
        doc="""The operating system as identified by Perforce.

        Typical values:
          - C{'NT'} for Windows platforms
          - C{'UNIX'} for Linux and Cygwin platforms

        @type: C{str}
        """
        def fget(self):
            return self._client.getOs()
        return (fget, None, None, doc)

    @attribute
    def password():
        doc="""The password to use for running the next command.

        May be set to the Perforce user's password or a valid ticket identifier
        returned from the 'p4 login' command. If a password or ticket is not
        provided then a ticket value is obtained from the P4TICKETS file.

        Defaults to the value in the P4CONFIG file if one exists, otherwise to
        the value of the P4PASSWD environment variable, otherwise to the value
        in the registry, otherwise to ''.

        @type: C{str} or C{unicode}

        @see: L{ticketFile}
        """
        def fget(self):
            return self._client.getPassword()
        def fset(self, value):
            self._client.setPassword(value)
        return (fget, fset, None, doc)

    @attribute
    def port():
        doc="""The Perforce server address and port number.

        Defaults to the value in the P4CONFIG file if one exists, otherwise to
        the value of the P4PORT environment variable, otherwise to the value in
        the registry, otherwise to 'perforce:1666'.

        @note: Must be set prior to calling L{connect()} to have an effect.

        @type: C{str} (may be set using C{unicode})
        """
        def fget(self):
            return self._client.getPort()
        def fset(self, value):
            self._client.setPort(value)
        return (fget, fset, None, doc)

    @attribute
    def prog():
        doc="""The client program name to identify this connection with.

        The value set here shows up when running the 'p4 monitor' command and
        in the Perforce server logs.

        @type: C{str} or C{unicode}
        
        @note: Setting this value has an effect only after a connection has
        been made to the Perforce server.
        """
        def fset(self, value):
            self._client.setProg(value)
        return (None, fset, None, doc)

    @attribute
    def ticketFile():
        doc="""The P4TICKETS file to use for this connection.

        This attribute may be set to specify the file to store the Perforce
        authentication tickets obtained by running the 'p4 login' command.

        The path should be an absolute path.

        @type: C{str} or C{unicode}
        """
        def fset(self, value):
            self._client.setTicketFile(value)
        return (None, fset, None, doc)

    if float(perforce.api.version) < 2005.1:
        del ticketFile

    @attribute
    def user():
        doc="""The Perforce username to use for running the next command.

        Defaults to the value in the P4CONFIG file if one exists, otherwise to
        the value of the P4USER environment variable, otherwise to the value in
        the registry, otherwise to the o/s username of the currently logged in
        user.

        @type: C{str} or C{unicode}
        """
        def fget(self):
            return self._client.getUser()
        def fset(self, value):
            self._client.setUser(value)
        return (fget, fset, None, doc)

    @attribute
    def version():
        doc="""The client program version to identify this connection with.

        The value set here shows up when running the 'p4 monitor' command and
        in the Perforce server logs.

        @type: C{str} or C{unicode}

        @note: Setting this value has an effect only after a connection has
        been made to the Perforce server.
        @note: Only available for Perforce 2005.2 or later clients.

        @see: L{prog}
        """
        def fset(self, value):
            self._client.setVersion(value)
        return (None, fset, None, doc)

    if float(perforce.api.version) < 2005.2:
        del version

    def connect(self, **options):
        """Connect to the Perforce server.

        @note: The L{port} and L{api} properties must be set before
        calling this method to have an effect.

        @param options: Attributes to set after the connection is established.

        @keyword prog: The program to identify as on this connection.
        Convenience notation for setting L{self.prog} after connecting.
        @type prog: C{str} or C{unicode}

        @keyword version: The version of the program to identify as on this
        conenction. Convenience notation for setting L{self.version} after
        connecting.
        @type version: C{str} or C{unicode}

        @raise ConnectionFailed: If the client could not connect to the
        Perforce server.
        """
        if not self._connected:
            self._client.setProtocol("tag","")
            self._client.setProtocol("specstring","")
            self._client.init()
            self._connected = True
            if 'prog' in options:
                self.prog = options['prog']
            if 'version' in options and hasattr(self, 'version'):
                self.version = options['version']

    def disconnect(self):
        """Disconnect from the Perforce server.

        If not connected then calling this method is a no-op.
        """
        if self._connected:
            self._client.final()
            self._connected = False

    def run(self, command, *args, **kwargs):
        """Run a command on the connected Perforce server.

        Example::
          | c.run('sync', '-f', 'foo.txt#3', client='my-client')

        @param command: The Perforce command to run.
        @type command: C{str} or C{unicode}
        
        @param args: The arguments to pass to the Perforce command.
        @type args: C{tuple} of C{str} or C{unicode}

        @keyword ui: Specify the ClientUser object to process the Perforce
        command events. Use of this parameter overrides the C{input} and
        C{output} parameters.
        @type ui: L{perforce.api.ClientUser}

        @keyword input: Specify the input to give to the Perforce command.
            Pass some input to this parameter when running commands using the
            -i flag or running 'passwd' or 'login' commands.
        @type input: C{str}, C{unicode}, L{perforce.forms.Form} or C{list} of
        C{str} or C{unicode}

        @keyword output: Specify an alternative output handler to be called
            when output of the command is received from the Perforce server.
            If not supplied then a L{perforce.results.Results} object is used.
        @type output: adaptable to L{perforce.results.IOutputConsumer}

        @keyword charset: The override of the charset attribute to use for
            running this command.
        @type charset: C{str}, L{perforce.CharSet} or C{NoneType}

        @keyword client: The override of the client attribute to use for
            running this command.
        @type client: C{str} or C{unicode}

        @keyword cwd: The override of the cwd attribute to use for running this
            command.
        @type cwd: C{str} or C{unicode}

        @keyword host: The override of the host attribute to use for running
            this command.
        @type host: C{str}

        @keyword language: The override of the language attribute to use for
            running this command.
        @type language: C{str} or C{unicode}

        @keyword user: The override of the user attribute to use for running
            this command.
        @type user: C{str} or C{unicode}

        @keyword password: The override of the password attribute to use for
            running this command.
        @type password: C{str} or C{unicode}

        @return: Returns the value passed to the C{output} parameter if
        provided, otherwise returns a L{perforce.results.Results} object
        populated with the output of running the command.

        @raise ConnectionDropped: if the connection to the Perforce
        server was dropped before the command completed.

        @raise protocols.AdaptationFailure: If C{output} does not support the
        L{perforce.results.IOutputConsumer} interface.
        """

        if 'output' in kwargs:
            output = kwargs['output']
        else:
            from perforce.results import Results
            output = Results()
            
        if 'input' in kwargs:
            input = kwargs['input']
        else:
            input = None

        overridables = ['charset', 'client', 'cwd', 'host',
                        'language', 'user', 'password']

        overrides = {}
        for overridable in overridables:
            if overridable in kwargs:
                overrides[overridable] = kwargs[overridable]

        # Save the original values for later restoration
        originals = self._saveOverrides(overrides)

        # Apply any overrides supplied
        self._applyOverrides(overrides)
        try:
            if 'ui' in kwargs:
                # The user has provided a custom ClientUser instance
                ui = kwargs['ui']
                result = ui
                
            else:
                # Run the command using synchronous output
                ui = _SynchronousClientUser(input, output)
                result = output
                
            self._client.setArgs(args)
            try:
                self._client.run(command, ui)
            except perforce.api.ConnectionDropped:
                self._connected = False
                raise
        finally:
            # Restore any overridden values
            self._applyOverrides(originals)
        return result

    def _saveOverrides(self, overrides):
        """Save the environment before overriding with overrides.

        Any writable attribute of this class is able to be overridden.

        @param overrides: A dictionary of the overrides to be applied.
        @type overrides: C{dict}

        @return: A dictionary of overrides to be applied to restore the
        environment to the current values after the C{overrides} have
        been applied.
        @rtype: C{dict}
        """
        originals = {}
        if 'cwd' in overrides:
            # Need to save everything if the 'cwd' changes as it can
            # potentially find a new P4CONFIG file and cause changes to
            # all of the other parameters.
            originals['charset'] = self.charset
            originals['client'] = self.client
            originals['cwd'] = self.cwd
            originals['host'] = self.host
            originals['language'] = self.language
            originals['password'] = self.password
            originals['port'] = self.port
            originals['user'] = self.user
        else:
            # Save only the overrided values that are changing
            for override in overrides:
                originals[override] = getattr(self, override)
        return originals

    def _applyOverrides(self, overrides):
        """Override the environment with the dictionary of overrides.

        Any writable attribute of this class is able to be overridden.

        @param overrides: A dictionary of attribute names to values to
        override.
        @type overrides: C{dict}
        """
        # Apply the charset first so that the other values are interpreted
        # consistently.
        if 'charset' in overrides:
            self.charset = overrides['charset']
        
        # Apply the 'cwd' override next so that other overrides aren't
        # overridden by variables in a P4CONFIG file.
        if 'cwd' in overrides:
            previousCharset = self.charset
            self.cwd = overrides['cwd']
            if self.charset != previousCharset:
                # Reset the charset to force a call to setTrans()
                self.charset = self.charset

        for override in overrides:
            if override not in ['cwd', 'charset']:
                setattr(self, override, overrides[override])

class _SynchronousClientUser(perforce.api.ClientUser):
    """Class for translating L{perforce.api.ClientUser} calls to synchronous
    L{perforce.results.IOutputConsumer} calls.

    Use instances of this class with L{perforce.api.ClientApi.run} to provide
    input to Perforce commands and to receive output from Perforce commands as
    calls to a L{perforce.results.IOutputConsumer} object.

    Each instance should only be used for running a single command.
    """

    def __init__(self, input, output):
        """Construct a new L{perforce.api.ClientUser} adapter.

        @param input: A string or object convertible to a string (such as a
        L{perforce.forms.Form}) to be given as input for the command to be
        run.
        @type input: C{str} or C{unicode}

        @param output: The output consumer that is to receive output from
        running the command.
        @type output: adaptable to L{perforce.results.IOutputConsumer}

        @raise protocols.AdaptationFailure: If C{output} does not support the
        L{perforce.results.IOutputConsumer} interface.
        """
        from perforce.results import IOutputConsumer
        self._output = IOutputConsumer(output)
        
        if input is None:
            self._input = None
        elif isinstance(input, list):
            # Take a copy as we're going to modify it
            self._input = list(input)
        else:
            self._input = [input]

    def inputData(self, err):
        if self._input is not None:
            if self._input:
                if isinstance(err.format(), unicode):
                    return unicode(self._input.pop(0))
                else:
                    return str(self._input.pop(0))
            else:
                self._input = None
            
        from perforce.api import ErrorSeverity
        err.set(ErrorSeverity.FAILED, "No input data available")
        return None

    def prompt(self, message, noEcho, err):
        return self.inputData(err)

    def outputError(self, msg):
        # Some Perforce commands still call outputError rather than
        # outputMessage, so we construct our own perforce.api.Error
        # object to pass to outputMessage.
        severity = perforce.api.ErrorSeverity.FAILED
        err = perforce.api.Error()
        err.set(severity, msg)
        self.outputMessage(err)

    def outputInfo(self, level, msg):
        # Some Perforce commands still call outputInfo rather than
        # outputMessage, so we construct our own perforce.api.Error
        # object to pass to outputMessage.
        severity = perforce.api.ErrorSeverity.INFO
        err = perforce.api.Error()
        err.set(severity, msg)
        self.outputMessage(err)

    def outputMessage(self, msg):
        self._output.outputMessage(msg)

    def outputStat(self, stat):
        if 'specdef' in stat:
            specdef = stat['specdef']
            if 'data' in stat:
                data = stat['data']
            else:
                # Perforce 2005.2 and later has already partially parsed
                # the form data into a dictionary with a key/value pair for
                # each line of the form.
                
                # Take a copy and remove some unnecessary fields so they don't
                # confuse the form parsing logic.
                data = stat.copy()
                del data['specdef']
                if 'func' in data:
                    del data['func']
                    
            from perforce.forms import Form
            form = Form(specdef, data)
            self._output.outputForm(form)
        else:
            self._output.outputRecord(stat)

    def outputBinary(self, data):
        self._output.outputBinary(data)

    def outputText(self, data):
        self._output.outputText(data)

    def finished(self):
        self._output.finished()

# Get rid of temporary helper definitions
del attribute
