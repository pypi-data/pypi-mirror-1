"""perforce.results - Helper classes for managing results of Perforce commands.
"""

__all__ = ['FileData',
           'FileLog',
           'FileRevision',
           'Integration',
           'Results',
           'IOutputConsumer',
           'ResultsOutputConsumer',
           ]

import protocols

class FileData(object):
    """Helper class for storing Perforce file data as a string.

    @ivar isBinary: Flag indicating if the file data contains binary or text
    data.
    @type isBinary: C{boolean}

    @ivar data: The file data bytes.
    @type data: C{str}
    """

    __slots__ = ['isBinary', 'data']
    
    def __init__(self, data, isBinary):
        self.isBinary = isBinary
        self.data = data

class FileLog(object):
    """A utility class for storing the results of a 'p4 filelog' command.

    A filelog consists of a list of L{FileRevision} objects, one for each
    revision of a particular depot file.

    @ivar depotFile: The path of the file in the repository.
    @type depotFile: C{str} or C{unicode}

    @ivar revisions: A list of C{FileRevision} objects for this depotFile.
    @type revisions: C{list} of C{FileRevision} objects.

    @see: L{FileRevision}, L{Integration}
    """

    __slots__ = ['depotFile', 'revisions']

    def __init__(self, depotFile, revisions):
        """Construct a FileLog object.
        """
        self.depotFile = depotFile
        self.revisions = revisions

    @staticmethod
    def parseRecord(record):
        """Construct a populated FileLog object from a 'p4 filelog' record.

        Example::
          | from perforce.connection import Connection
          | from perforce.results import FileLog
          | c = Connection()
          | c.connect()
          | results = c.run('filelog', '//depot/some/file.txt')
          | fileLog = FileLog.parseRecord(results.records[0])

        @param record: The record passed via L{IOutputConsumer.outputRecord}.
        @type record: C{dict}
        """
        depotFile = record['depotFile']
        revisions = []
        
        i = 0
        while 'rev%i' % i in record:
            rev = int(record['rev%i' % i])
            change = int(record['change%i' % i])
            action = record['action%i' % i]
            type = record['type%i' % i]
            user = record['user%i' % i]
            client = record['client%i' % i]
            desc = record['desc%i' % i]
            time = int(record['time%i' % i])
            integrations = []
            
            j = 0
            while 'how%i,%i' % (i, j) in record:
                how = record['how%i,%i' % (i, j)]
                file = record['file%i,%i' % (i, j)]
                srev = record['srev%i,%i' % (i, j)]
                erev = record['erev%i,%i' % (i, j)]
                integ = Integration(how, file, srev, erev)
                integrations.append(integ)
                j += 1

            fileRev = FileRevision(rev, change, action, type, user,
                                   client, desc, time, integrations)
            revisions.append(fileRev)
            i += 1

        return FileLog(depotFile, revisions)

class FileRevision(object):
    """Information about a single revision of a file.

    The file revision contains information about the change for that revision
    as well as a list of L{Integration} records that provide information about
    the integrations that the file revision was involved in.

    @ivar rev: The revision of this file.
    @type rev: C{int}

    @ivar change: The change number that this file revision belongs to.
    @type change: C{int}

    @ivar action: The action performed on the file in this revision.
    ie. 'add', 'edit', 'delete', 'integrate', 'branch' or 'import'
    @type action: C{str} or C{unicode}

    @ivar type: The Perforce file type of the file in this revision.
    eg 'text', 'text+kmx', 'binary', 'unicode'
    @type type: C{str} or C{unicode}

    @ivar user: The username of the user who submitted the change for this
    file revision.
    @type user: C{str} or C{unicode}

    @ivar client: The name of the client the change for this file revision
    was submitted from.
    @type client: C{str} or C{unicode}

    @ivar desc: The description of the change this file revision belongs to.
    @type desc: C{str} or C{unicode}

    @ivar time: The time of this change as a POSIX timestamp.
    ie. The nubmer of seconds since 1970/01/01 00:00 UTC.
    This can be converted to local time by constructing a C{datetime.datetime}
    object using C{datetime.fromtimestamp()}.
    @type time: C{int}

    @see: L{FileLog}, L{Integration}
    """

    __slots__ = ['rev', 'change', 'action', 'type', 'user', 'client', 'desc',
                 'time', 'integrations']

    def __init__(self, rev, change, action, type, user,
                 client, desc, time, integrations):
        self.rev = rev
        self.change = change
        self.action = action
        self.type = type
        self.user = user
        self.client = client
        self.desc = desc
        self.time = time
        self.integrations = integrations

class Integration(object):
    """Information about a single file integration.

    @ivar how: The type of this integration record.
    Typically one of '[branch/copy/edit/ignore/merge] [from/to]'.
    @type how: C{str} or C{unicode}

    @ivar file: The path to the other file involved in this integration.
    @type file: C{str} or C{unicode}

    @ivar srev: The start revision of the C{file} being integrated.
    Typically something like '#none' or '#123'
    @type srev: C{str} or C{unicode}

    @ivar erev: The end revision of the C{file} being integrated.
    Typically something like '#123'.
    @type erev: C{str} or C{unicode}

    @see: L{FileLog}, L{FileRevision}
    """

    __slots__ = ['how', 'file', 'srev', 'erev']

    def __init__(self, how, file, srev, erev):
        self.how = how
        self.file = file
        self.srev = srev
        self.erev = erev

class Results(object):
    """A utility class for storing the results of a Perforce command.

    This class is adaptable to the IOutputConsumer class.

    @ivar all: A list of all events (messages, records, fileChunks and forms)
    output from a Perforce command in the order they occurred.
    @type all: C{list} of L{perforce.Message}, L{perforce.forms.Form}, C{dict}
    and L{FileData} objects.

    @ivar messages: A list of all messages output from a Perforce command
    in the order they occurred.
    @type messages: C{list} of L{perforce.Message} objects.

    @ivar infos: A list of all info messages output from a Perforce command
    in the order they occurred. Info messages are typically output when
    something succeeds.
    @type infos: C{list} of L{perforce.Message} objects.

    @ivar warnings: A list of all warning messages output from a Perforce
    command. Warning messages are typically output when an operation fails
    partially or in a non-critical way.
    eg. a C{'sync'} operation reporting that 'all file(s) are up to date'.
    @type warnings: C{list} of L{perforce.Message} objects.

    @ivar errors: A list of all error messages output from a Perforce command.
        Error messages are output when an operation fails for some reason.
    @type errors: C{list} of L{perforce.Message} objects.

    @ivar records: A list of the records output from a Perforce command.
    Records are typically output from commands that request information
    about Perforce entities.
    @type records: C{list} of C{dict} objects.

    @ivar fileChunks: A list of file chunks output from a Perforce command.
    File chunks are typically output from 'print' commands. A file chunk
    is either text or binary.
    @type fileChunks: C{list} of L{FileData} objects.

    @ivar forms: A list of forms output from a Perforce command.
    Typically only one form is output per command, however a list is used
    here so that the same L{Results} object can be used for multiple commands.
    @type forms: C{list} of L{perforce.forms.Form} objects.
    """

    __slots__ = ['all',
                 'messages', 'infos', 'warnings', 'errors',
                 'records',
                 'fileChunks',
                 'forms']

    def __init__(self):
        self.all = []        # All results (mixed data types)
        self.messages = []   # All messages (perforce.Message objects)
        self.infos = []      # Info messages (perforce.Message objects)
        self.warnings = []   # Warning messages (perforce.Message objects)
        self.errors = []     # Error messages (perforce.Message objects)
        self.records = []    # Data records (dictionaries)
        self.fileChunks = [] # File data chunks (FileData objects)
        self.forms = []      # Form (perforce.forms.Form objects)

class IOutputConsumer(protocols.Interface):
    """This interface class declares the interface that consumers of
    Perforce command output must provide.
    """

    def outputMessage(message):
        """Output a Perforce message.

        @param message: The info, warning or error message being output by
        the Perforce command. The kind of message is determined by calling
        the C{message.is*()} methods. The textual representation of the message
        is obtainable by C{message.format()}.
        @type message: L{perforce.api.Error}
        """

    def outputRecord(record):
        """Output a Perforce data record.

        @param record: The data record to output. The fields of the record
        are stored in key/value pairs of the dictionary. The contents of
        the record depend on the command being run.
        @type record: C{dict}
        """

    def outputForm(form):
        """Output a Perforce form.

        @param form: The form to output. This method is typically called when
        running a form-based command with the '-o' flag.
        @type form: L{perforce.forms.Form}
        """

    def outputBinary(data):
        """Output a chunk of binary file data.

        Output of large files may call this method several times to allow
        output of the file in chunks rather than storing it all in memory.
        
        @note: No end-of-line conversion should be performed on this data when
        outputting it.

        @param data: The chunk of file data to output. The string may be
        interpreted as an array of bytes.
        @type data: C{str}
        """

    def outputText(data):
        """Output a chunk of binary file data.

        Output of large files may call this method several times to allow
        output of the file in chunks rather than storing it all in memory.
        
        @note: End-of-line conversion may be performed on this data when
        outputting it.

        @param data: The chunk of file data to output. The string may be
        interpreted as an array of bytes.
        @type data: C{str}
        """

    def finished():
        """Called when the command has finished running."""

class ResultsOutputConsumer(object):
    """An L{IOutputConsumer} that places all output into a L{Results} object.

    The results are obtainable via the L{results} attribute of instances.

    @ivar results: The object that receives the results of running a command.
    @type results: L{Results}
    """

    protocols.advise(
        instancesProvide=[IOutputConsumer],
        asAdapterForTypes=[Results],
        )

    def __init__(self, results=None):
        if results is None:
            self.results = Results()
        else:
            self.results = results

    def outputMessage(self, message):
        self.results.all.append(message)
        self.results.messages.append(message)
        if message.isInfo():
            self.results.infos.append(message)
        elif message.isWarning():
            self.results.warnings.append(message)
        elif message.isError():
            self.results.errors.append(message)

    def outputRecord(self, record):
        self.results.all.append(record)
        self.results.records.append(record)

    def outputForm(self, form):
        self.results.all.append(form)
        self.results.forms.append(form)

    def outputBinary(self, data):
        fileData = FileData(data, isBinary=True)
        self.results.all.append(fileData)
        self.results.fileChunks.append(fileData)

    def outputText(self, data):
        fileData = FileData(data, isBinary=False)
        self.results.all.append(fileData)
        self.results.fileChunks.append(fileData)

    def finished(self):
        pass
