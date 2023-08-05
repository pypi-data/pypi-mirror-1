"""perforce.async.connection - Asynchronous Perforce connection API.

The asynchronous API uses Twisted to handle asynchronous notification of
operations.
"""

__all__ = [
    'Connection',
    'ConnectionFailed',
    'ConnectionDropped',
    'connectPerforce',
    ]

import perforce.api
from perforce.api import ConnectionFailed, ConnectionDropped

_logContext = {'system' : 'Perforce'}

def attribute(fun):
    """Helper decorator for turning methods into properties."""
    return property(*fun())

class Connection(object):
    """A Perforce connection that allows asynchronous running of commands.

    Use instances of this class to run commands on the Perforce server
    asynchronously, returning twisted Deferred objects.

    Only one command executes using this connection at any one time, however,
    many connections may be simultaneously executing on separate threads in the
    Twisted thread pool.

    @see: L{connectPerforce}
    """

    __slots__ = ['_client', '_connected', '_defaults', '_isRunning',
                 '_pendingDisconnect', '_pendingCommands']

    def __init__(self, client):
        """Construct a Connection object from an already connected ClientApi.

        @param client: A connected ClientApi object.
        @type client: L{perforce.api.ClientApi}

        @note: Instances of this class should be created by calling the
        L{connectPerforce} function.

        @see: L{connectPerforce}
        """
        self._client = client
        self._connected = True
        self._pendingDisconnect = False
        self._defaults = {
            'server' : client.getProtocol('server2'),
            'nocase' : client.getProtocol('nocase'),
            'charset' : client.getCharset(),
            'client' : client.getClient(),
            'cwd' : client.getCwd(),
            'host' : client.getHost(),
            'language' : client.getLanguage(),
            'os' : client.getOs(),
            'password' : client.getPassword(),
            'port' : client.getPort(),
            'user' : client.getUser(),
            }
        self._pendingCommands = []
        self._isRunning = False

    def __del__(self):
        # Disconnect if we aren't already disconnected.
        if self._connected:
            from twisted.python import log
            log.msg("disconnecting from Perforce server",
                    **_logContext)
            self._client.final()

    @attribute
    def server():
        doc="""The Perforce server protocol version used by the connection.

        @type: C{str}

        @note: Can only be queried after running a command on this connection.

        @see: L{perforce.connection.Connection.server} for a list of the values
        and their corresponding Perforce server versions.
        """
        def fget(self):
            return self._defaults['server']
        return (fget, None, None, doc)

    @attribute
    def nocase():
        doc="""Flag indicating whether the server is case insensitive.

        @type: C{boolean}

        @note: Can only be queried after running a command on this connection.
        
        @see: L{server}
        """
        def fget(self):
            if self._defaults['nocase']:
                return True
            else:
                return False
        return (fget, None, None, doc)

    @attribute
    def charset():
        doc="""The default charset used for Perforce unicode files.

        This value may be overridden on a per-command basis by passing a
        value to the named 'charset' argument of run().

        For example::
          | c.run('sync', charset='utf8')

        @type: C{str} (may be set with C{unicode})
        """
        def fget(self):
            return self._defaults['charset']
        return (fget, None, None, doc)

    @attribute
    def client():
        doc="""The default Perforce client to use when running client commands.

        This value may be overridden on a per-command basis by passing the
        new client value to the named 'client' argument of run().

        For example::
          | c.run('sync', client='my-client')

        @type: C{str} or C{unicode}
        """
        def fget(self):
            return self._defaults['client']
        return (fget, None, None, doc)

    @attribute
    def cwd():
        doc="""The default working directory for running client commands.

        This value may be overridden on a per-command basis by passing the
        new working directory to the the named 'cwd' argument of run().

        For example::
          | c.run('sync', 'foo.h',
          |       cwd='/path/to/include')

        @type: C{str} or C{unicode}
        """
        def fget(self):
            return self._defaults['cwd']
        return (fget, None, None, doc)

    @attribute
    def host():
        doc="""The hostname of the local machine as identified by Perforce.

        @type: C{str} (may be set with C{unicode})
        
        @see: L{perforce.connection.Connection.host}
        """
        def fget(self):
            return self._defaults['host']
        return (fget, None, None, doc)

    @attribute
    def language():
        doc="""The language to use for Perforce messages.

        @type: C{str} or C{unicode}
        @see: L{perforce.connection.Connection.language}
        """
        def fget(self):
            return self._defaults['language']
        return (fget, None, None, doc)

    @attribute
    def os():
        doc="""The operating system as identified by Perforce.

        @type: C{str}
        @see: L{perforce.connection.Connection.os}
        """
        def fget(self):
            return self._defaults['os']
        return (fget, None, None, doc)

    @attribute
    def password():
        doc="""The default password to use to authenticate the Perforce user.

        This value may be overridden on a per-command basis by passing the
        new password to the named 'password' parameter of run().
        The ticket identifier (obtained from 'p4 login') may also be passed
        as the password for servers that require ticket-based authentication.

        For example::
          | c.run('user', '-d', 'joe',
          |        user='p4admin',
          |        password='thePassword')

        @type: C{str} or C{unicode}
        @see: L{perforce.connection.Connection.password}
        """
        def fget(self):
            return self._defaults['password']
        return (fget, None, None, doc)
    
    @attribute
    def port():
        doc="""The address and port of the connected Perforce server.

        @type: C{str} (may be set with C{unicode})
        @see: L{perforce.connection.Connection.port}
        """
        def fget(self):
            return self._defaults['port']
        return (fget, None, None, doc)

    @attribute
    def user():
        doc="""The default Perforce user name to use for running commands.
        
        This value may be overridden on a per-command basis by passing
        the new user name to the named 'user' argument of run().

        For example::
          | c.run('login', user='joe',
          |       input='thePassword')

        @type: C{str} or C{unicode}
        @see: L{perforce.connection.Connection.user}
        """
        def fget(self):
            return self._defaults['user']
        return (fget, None, None, doc)

    def disconnect(self):
        """Disconnect from the server once all pending commands have finished.

        @note: Subsequent calls to L{run} will fail with L{ConnectionDropped}.
        """
        if self._connected:
            if self._isRunning:
                # Set a flag to disconnect at a later time
                self._pendingDisconnect = True
            else:
                # Disconnect now
                from twisted.python import log
                log.msg("disconnecting from Perforce server",
                        **_logContext)
                self._connected = False
                from twisted.internet import threads
                threads.deferToThread(self._client.final)
        
    def run(self, command, *args, **kwargs):
        """Run a Perforce command asynchronously.

        Connection parameters may be overridden on a per-command basis by
        specifying them as named parameters: ie. charset, client, cwd,
        language, user and password.

        @param command: The Perforce command to execute.
        @type command: C{str} or C{unicode}

        @param args: Arguments to provide to the Perforce command.
        @type args: C{tuple} of C{str} or C{unicode}

        @param kwargs: Additional parameters to provide to the command.

        @keyword input: Input to provide to the command (such as form
        contents or passwords). Multiple inputs may be specified by passing
        a list of values (useful for handling 'p4 passwd' prompts).
        @type input: convertible to C{str}, C{unicode} or C{list} of same

        @keyword output: An object that will receive the output of the command.
        If not provided then a L{perforce.results.Results} object will be used.
        Callbacks will be made on this object in the main thread.
        @type output: adaptable to L{perforce.results.IOutputConsumer}

        @keyword charset: Optional override value for the L{charset}
        environment variable for this command only.
        @type charset: C{perforce.api.CharSet}, C{str}, C{unicode} or C{None}

        @keyword client: Optional override value for the L{client} environment
        variable for this command only.
        @type client: C{str} or C{unicode}

        @keyword cwd: Optional override value for the L{cwd} environment
        variable for this command only.
        @type cwd: C{str} or C{unicode}

        @keyword user: Optional override value for the L{user} environment
        variable for this command only.
        @type user: C{str} or C{unicode}

        @keyword password: Optional override value for th L{password}
        environment variable for this command only.
        @type password: C{str} or C{unicode}

        @return: A deferred that fires with the C{output} object when the
        command finishes executing.

        @warning: This method should only ever be called from the Twisted main
        thread.
        """

        from perforce.results import Results
        from twisted.internet import defer

        deferred = defer.Deferred()
        
        overrideKeys = ['user', 'password', 'client', 'charset', 'cwd']
        overrides = {}
        for param in overrideKeys:
            if param in kwargs:
                overrides[param] = kwargs[param]

        commandState = {
            'command' : command,
            'args' : args,
            'deferred' : deferred,
            'overrides' : overrides,
            'defaults' : self._defaults,
            'input' : ('input' in kwargs and kwargs['input']) or None,
            'output' : ('output' in kwargs and kwargs['output']) or None,
            }

        if not self._connected or self._pendingDisconnect:
            # The connection has been dropped or is about to be dropped.
            # Fail this command now so we don't queue up any more commands.
            failure = defer.failure.Failure(ConnectionDropped)
            reactor.callLater(0, deferred.errback, failure)
        else:
            # Queue the command for later execution
            from twisted.python import log
            log.msg("queuing Perforce command 'p4 %s'" %
                    ' '.join([command] + list(args)),
                    **_logContext)
            
            self._pendingCommands.append(commandState)

            # Start the next command if not running one already.
            if not self._isRunning:
                self._processNextCommand()

        return deferred

    def _processNextCommand(self):
        assert not self._isRunning
        assert self._pendingCommands

        if not self._connected:
            # The connection has been dropped, fail all pending commands.
            from perforce.api import ConnectionDropped
            from twisted.internet import defer, reactor
            
            while self._pendingCommands:
                commandState = self._pendingCommands.pop(0)
                deferred = commandState['deferred']
                failure = defer.failure.Failure(ConnectionDropped)
                reactor.callLater(0, deferred.errback, failure)
        else:
            # Get the next command and schedule it for execution
            commandState = self._pendingCommands.pop(0)

            from twisted.internet import reactor
            reactor.callLater(0, self._startCommand, commandState)
            
            self._isRunning = True

    def _startCommand(self, commandState):

        command = commandState['command']
        args = commandState['args']

        from twisted.python import log
        log.msg("starting Perforce command 'p4 %s'" %
                ' '.join([command] + list(args)),
                **_logContext)

        from twisted.internet import threads
        d = threads.deferToThread(_synchronousRun,
                                  self._client,
                                  commandState)

        # Want to peek any errors so we can update our connected state in
        # the case that the connection was dropped running a command.
        def connectionDroppedHandler(reason):
            from perforce.api import ConnectionDropped
            reason.trap(ConnectionDropped)
            self._connected = False
            return reason
        d.addErrback(connectionDroppedHandler)

        # Peek the result to flag the command as complete.
        # Start the next pending command if needed.
        def commandFinishedHandler(result):
            from twisted.python import log
            log.msg("finished Perforce command", **_logContext)

            # Update the protocol parameters if this is our first command
            if self._defaults['server'] == '0':
                self._defaults['server'] = self._client.getProtocol('server2')
                self._defaults['nocase'] = self._client.getProtocol('nocase')
                
            self._isRunning = False
            if self._pendingCommands:
                self._processNextCommand()
            elif self._pendingDisconnect:
                self.disconnect()
            return result
        d.addBoth(commandFinishedHandler)

        # Trigger the client's callback when the command is finished.
        d.chainDeferred(commandState['deferred'])

class _AsynchronousClientUser(perforce.api.ClientUser):

    def __init__(self, input, output):
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
                return str(self._input.pop(0))
            else:
                self._input = None

        from perforce.api import ErrorSeverity
        err.set(ErrorSeverity.FAILED, "No more input data")
        return None

    def prompt(self, message, noEcho, err):
        return self.inputData(err)

    def outputInfo(self, level, message):
        # Some perforce commands still call outputInfo rather than
        # outputMessage.
        # Convert it back to an Error object and pass to outputMessage.
        severity = perforce.api.ErrorSeverity.INFO
        err = perforce.api.Error()
        err.set(severity, message)
        
        from twisted.internet import reactor
        reactor.callFromThread(self._output.outputMessage, err)

    def outputError(self, message):
        # Some perforce commands still call outputError rather than
        # outputMessage.
        # Convert it back to an Error object and pass to outputMessage.
        severity = perforce.api.ErrorSeverity.FAILED
        err = perforce.api.Error()
        err.set(severity, message)
        
        from twisted.internet import reactor
        reactor.callFromThread(self._output.outputMessage, err)

    def outputMessage(self, message):
        from twisted.internet import reactor
        reactor.callFromThread(self._output.outputMessage, message)

    def outputStat(self, data):
        from twisted.internet import reactor
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
            reactor.callFromThread(self._output.outputForm, form)
        else:
            reactor.callFromThread(self._output.outputRecord, data)

    def outputBinary(self, data):
        from twisted.internet import reactor
        reactor.callFromThread(self._output.outputBinary, data)

    def outputText(self, data):
        from twisted.internet import reactor
        reactor.callFromThread(self._output.outputText, data)

    def finished(self):
        from twisted.internet import reactor
        reactor.callFromThread(self._output.finished)

def _synchronousRun(clientApi, commandState):
    """Run a command on the Perforce client synchronously.

    This function is designed to be run in a separate thread from the
    Twisted main thread.
    """

    from perforce.api import CharSet

    overrides = commandState['overrides']

    if 'charset' in overrides:
        cs = CharSet(overrides['charset'])
        if cs.codec and cs.codec.lower().startswith('utf_16'):
            # Can only use UTF-16 for file content
            utf8 = CharSet.UTF_8
            clientApi.setTrans(utf8, cs, utf8, utf8)
        else:
            clientApi.setTrans(cs, cs, cs, cs)

        if 'cwd' in overrides:
            clientApi.setCwd(overrides['cwd'])

        clientApi.setCharset(overrides['charset'])
    elif 'cwd' in overrides:
        clientApi.setCwd(overrides['cwd'])

        # Update with either the default or P4CONFIG value for P4CHARSET
        cs = CharSet(clientApi.getCharset())
        if cs.codec and cs.codec.lower().startswith('utf_16'):
            # Can only use UTF-16 for file content
            utf8 = CharSet.UTF_8
            clientApi.setTrans(utf8, cs, utf8, utf8)
        else:
            clientApi.setTrans(cs, cs, cs, cs)

    if 'user' in overrides:
        clientApi.setUser(overrides['user'])

    if 'password' in overrides:
        clientApi.setPassword(overrides['password'])

    if 'client' in overrides:
        clientApi.setClient(overrides['client'])

    if 'language' in overrides:
        clientApi.setLanguage(overrides['language'])

    if 'host' in overrides:
        clientApi.setHost(overrides['host'])

    input = commandState['input']
    output = commandState['output']

    command = commandState['command']
    args = commandState['args']

    try:
        if output is None:
            from perforce.results import Results
            output = Results()
            from perforce.connection import _SynchronousClientUser
            ui = _SynchronousClientUser(input, output)
        else:
            ui = _AsynchronousClientUser(input, output)

        from twisted.python import log
        log.msg("running Perforce command 'p4 %s'" %
                ' '.join([command] + list(args)),
                **_logContext)
        
        clientApi.setArgs(args)
        clientApi.run(command, ui)
    finally:
        # Reset all the values back to the defaults
        defaults = commandState['defaults']
        
        if 'cwd' in overrides:

            # Restore the active charset first
            cs = CharSet(defaults['charset'])
            if cs.codec and cs.codec.lower().startswith('utf_16'):
                # Can only use UTF-16 for file content
                utf8 = CharSet.UTF_8
                clientApi.setTrans(utf8, cs, utf8, utf8)
            else:
                clientApi.setTrans(cs, cs, cs, cs)

            # Changing the 'cwd' could possibly reset all of the other
            # values if a P4CONFIG file is found. So we need to restore
            # all of the original values.
            clientApi.setCwd(defaults['cwd'])
            clientApi.setCharset(defaults['charset'])
            clientApi.setUser(defaults['user'])
            clientApi.setPassword(defaults['password'])
            clientApi.setClient(defaults['client'])
            clientApi.setLanguage(defaults['language'])
            clientApi.setHost(defaults['host'])
            
        else:
            # Restore the active charset first so that other values are
            # interpreted correctly.
            if 'charset' in overrides:
                cs = CharSet(defaults['charset'])
                if cs.codec and cs.codec.lower().startswith('utf_16'):
                    # Can only use UTF-16 for file content
                    utf8 = CharSet.UTF_8
                    clientApi.setTrans(utf8, cs, utf8, utf8)
                else:
                    clientApi.setTrans(cs, cs, cs, cs)
                clientApi.setCharset(defaults['charset'])

            if 'user' in overrides:
                clientApi.setUser(defaults['user'])

            if 'password' in overrides:
                clientApi.setPassword(defaults['password'])

            if 'client' in overrides:
                clientApi.setClient(defaults['client'])

            if 'language' in overrides:
                clientApi.setLanguage(defaults['language'])

            if 'host' in overrides:
                clientApi.setHost(defaults['host'])

    return output

def connectPerforce(port=None, host=None, language=None, charset=None,
                    cwd=None, client=None, user=None, password=None,
                    ticketFile=None, ignorePassword=False,
                    prog=None, version=None, api=None):
    """Connect to a Perforce server asynchronously.

    Accepts a number of parameters that let you specify the default values to
    use for Perforce environment variables for this connection.
    Some of these variables may also be overridden on a per-command basis via
    the L{Connection.run()} method.

    @param port: The Perforce server host and port string.
    If not specified then the P4PORT environment variable will be used.
    eg C{'perforce:1666'}
    @type port: C{str} or C{unicode}
    
    @param host: The local client's host name if it needs to be overridden.
    If not specified then the P4HOST environment variable or the machine name
    will be used.
    @type host: C{str} or C{unicode}

    @param language: The language to use for returned Perforce messages.
    If not specified then the P4LANGUAGE environment variable will be used.
    @type language: C{str} or C{unicode}

    @param charset: The character set to be used for encoding data sent to/from
    the Perforce server. Required to be set if connecting to a Unicode enabled
    server. If not set then the P4CHARSET environment variable will be used.
    @type charset: L{perforce.api.CharSet}, C{str}, C{unicode} or C{None}

    @param cwd: The current working directory to use for commands on this
    connection. If not set then the process' current working directory will
    be used.
    @type cwd: C{str} or C{unicode}

    @param client: The Perforce client to use for commands on this connection.
    If not set then the P4CLIENT environment variable will be used.
    @type client: C{str} or C{unicode}

    @param user: The Perforce username to use for this connection. If not set
    then the P4USER environment variable will be used.
    @type user: C{str} or C{unicode}

    @param password: The password to authenticate the Perforce user with.
    If not set then the P4PASSWD environment variable will be used.
    May also be the value of a ticket returned from a C{'p4 login'} command if
    the server supports tickets.
    @type password: C{str} or C{unicode}
    
    @param prog: The program name to identify the connection with.
    This shows up on the C{'p4 monitor'} command and Perforce server logs.
    @type prog: C{str} or C{unicode}

    @param version: The program version to identify the connection with.
    This shows up on the C{'p4 monitor'} command and Perforce server logs.
    Only supported for Perforce 2005.2 or later clients.
    @type version: C{str} or C{unicode}

    @param ticketFile: The path of the ticket file to use for this connection.
    All tickets used for authentication will be stored and retrieved from
    this file.
    @type ticketFile: C{str} or C{unicode}

    @param ignorePassword: Flag indicating whether passwords retrieved from
    the environment, registry or P4CONFIG file should be ignored.
    @type ignorePassword: C{boolean}

    @param api: The preferred Perforce protocol version to use for this
    connection. Setting this parameter can help to insulate code against
    protocol changes due to server upgrades.
    @type api: C{str}

    @return: A deferred that fires with the connection object once the
    connection has been established.
    @rtype: L{Connection}

    @raise ConnectionFailed: If the connection to the Perforce server failed.
    """
    
    from perforce.api import ClientApi, CharSet
    clientApi = ClientApi()

    # Make sure cwd is set first as it can lookup a new P4CONFIG file which
    # can override any previously set environment values. Also make sure that
    # the cwd value is interpreted using the charset override if specified.
    if charset is not None:

        # Use the override value for P4CHARSET
        cs = CharSet(charset)
        if cs.codec and cs.codec.lower().startswith('utf_16'):
            # Can only use UTF-16 for file content
            utf8 = CharSet.UTF_8
            clientApi.setTrans(utf8, cs, utf8, utf8)
        else:
            clientApi.setTrans(cs, cs, cs, cs)

        if cwd is not None:
            clientApi.setCwd(cwd)
            
        clientApi.setCharset(charset)
        
    elif cwd is not None:

        clientApi.setCwd(cwd)

        # Use either the default or P4CONFIG value for P4CHARSET
        cs = CharSet(clientApi.getCharset())
        if cs.codec and cs.codec.lower().startswith('utf_16'):
            # Can only use UTF-16 for file content
            utf8 = CharSet.UTF_8
            clientApi.setTrans(utf8, cs, utf8, utf8)
        else:
            clientApi.setTrans(cs, cs, cs, cs)
        
    if port is not None:
        clientApi.setPort(port)

    if host is not None:
        clientApi.setHost(host)

    if language is not None:
        clientApi.setLanguage(language)

    if client is not None:
        clientApi.setClient(client)

    if ticketFile is not None:
        clientApi.setTicketFile(ticketFile)

    if ignorePassword:
        clientApi.setIgnorePassword()

    if user is not None:
        clientApi.setUser(user)

    if password is not None:
        clientApi.setPassword(password)

    if api is not None:
        clientApi.setProtocol('api', api)

    clientApi.setProtocol('tag', '')
    clientApi.setProtocol('specstring', '')

    def synchronousConnect(client, prog, version):
        client.init()
        if prog is not None:
            client.setProg(prog)
        if version is not None:
            client.setVersion(version)
        return Connection(client)

    from twisted.python import log
    log.msg("connecting to Perforce server '%s'" % clientApi.getPort(),
            **_logContext)

    from twisted.internet import threads
    deferred = threads.deferToThread(synchronousConnect,
                                     clientApi, prog, version)
    return deferred

del attribute
