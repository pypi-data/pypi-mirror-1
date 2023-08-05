"""Asynchronous object-oriented interfaces for Perforce entities."""

__all__ = ['CommandError',
           'Client', 'User', 'Branch', 'Label', 'Change']

import re
import perforce.api
from perforce.objects import CommandError, FormObject

class Client(FormObject):
    """A Perforce client/workspace object."""

    __slots__ = ['__connection', '__name']

    def __new__(cls, connection, clientName):
        """Creates a Client based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use to
        query the client details.
        @type connection: L{perforce.connection.Connection} or
        L{perforce.async.connection.Connection}

        @param clientName: The name of the Perforce client to query.
        @type clientName: C{str} or C{unicode}

        @return: A deferred that fires with the L{Client} object once
        its form has been retrieved.
        @rtype: L{Client}

        @raise CommandError: If there was a Perforce error querying the client.
        """
        def handleResults(results):
            if results.errors or not results.forms:
                raise CommandError('p4 client -o %s' % clientName,
                                   results.messages)

            form = results.forms[0]
            self = object.__new__(cls)
            Client.__init__(self, connection, clientName, form)
            return self

        from twisted.internet import defer
        d = defer.maybeDeferred(connection.run, 'client', '-o', clientName)
        d.addCallback(handleResults)
        return d

    def __init__(self, connection, clientName, form):
        """Initialises the Client based on the form retrieved on the
        connection.

        @param connection: The connection to the Perforce server to use to
        query the client details.
        @type connection: L{perforce.connection.Connection} or
        L{perforce.async.connection.Connection}

        @param clientName: The name of the Perforce client to query.
        @type clientName: C{str} or C{unicode}

        @param form: The form object retrieved from the Perforce server.
        @type form: L{perforce.forms.Form}
        """
        FormObject.__init__(self, form)
        self.__connection = connection
        self.__name = clientName

    def save(self):
        """Save any changes made to the client on the Perforce server.

        @return: A deferred that fires with C{None} when the save operation
        completes.
        @rtype: C{None}

        @raise CommandError: If there was a Perforce error saving the client.
        """
        def handleResults(results):
            if results.errors:
                raise CommandError('p4 client -i',
                                   results.errors)

        from twisted.internet.defer import maybeDeferred
        d = maybeDeferred(self.__connection.run,
                          'client', '-i',
                          input=self._form)
        d.addCallback(handleResults)
        return d

    def sync(self, *fileRevisions, **options):
        """Sync the client workspace to the specified file revisions.

        If no file revisions are specified, then sync the entire workspace
        to the latest revision.

        @param fileRevisions: The file revisions to sync in this workspace.
        If no fileRevisions were specified then all files in the workspace are
        synced to the #head revision.
        @type fileRevisions: C{tuple} of C{str} or C{unicode}

        @keyword force: Pass as C{True} to force all named file revisions to
        be retransmitted rather than just those that are out of date.
        @type force: C{boolean}

        @return: The results of performing the sync operation in a deferred.
        @rtype: L{perforce.results.Results}

        @raise CommandError: If there was a Perforce error syncing the client.
        """
        force = False
        if 'force' in options:
            force = options['force']

        overrides = {'client' : self.__name}

        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'sync', '-f',
                              *fileRevisions,
                              **overrides)
        else:
            d = maybeDeferred(self.__connection.run,
                              'sync',
                              *fileRevisions,
                              **overrides)
        return d

    def delete(self, force=False):
        """Delete this client workspace from the Perforce repository.

        The client cannot normally be deleted when the client is locked.
        Passing force=True will allow the client owner or a Perforce user with
        admin privileges to forcibly delete a locked client.

        @note: This operation will not delete the files from the client's
        directory.

        @return: A deferred that fires when the operation completes
        successfully.

        @raise CommandError: If there was a Perforce error deleting the client.
        """
        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 client -d -f %s' % self.__name,
                                       results.errors)
                else:
                    raise CommandError('p4 client -d %s' % self.__name,
                                       results.errors)
        
        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'client', '-d', '-f', self.__name)
        else:
            d = maybeDeferred(self.__connection.run,
                              'client', '-d', self.__name)
        d.addCallback(handleResults)
        return d

class User(FormObject):
    """A Perforce user object."""

    __slots__ = ['__connection', '__name']

    def __new__(cls, connection, userName):
        """Creates a User based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        @type connection: L{perforce.connection.Connection}

        @param userName: The name of the user to query.
        @type userName: C{str} or C{unicode}

        @return: A deferred that fires with the L{User} object once its form
        has been retrieved.
        @rtype: L{User}

        @raise CommandError: If there was a Perforce error querying the user.
        """
        def handleResults(results):
            if results.errors or not results.forms:
                raise CommandError('p4 user -o %s' % userName,
                                   results.messages)

            form = results.forms[0]
            self = object.__new__(cls)
            User.__init__(self, connection, userName, form)
            return self

        from twisted.internet.defer import maybeDeferred
        d = maybeDeferred(connection.run, 'user', '-o', username)
        d.addCallback(handleResults)
        return d

    def __init__(self, connection, userName, form):
        """Initialises the User based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        @type connection: L{perforce.connection.Connection} or
        L{perforce.async.connection.Connection}

        @param userName: The name of the user to query.
        @type userName: C{str} or C{unicode}

        @param form: The form object retrieved from the Perforce server.
        @type form: L{perforce.forms.Form}
        """
        FormObject.__init__(self, form)
        self.__connection = connection
        self.__name = userName

    def save(self, force=False):
        """Save any changes made to the user to the Perforce server.

        By default a user can only update their own user specification.
        Specifying the C{force} parameter as C{True} allows users with
        C{'super'} access to modify other user's specifications and to
        modify the C{'Update'} field.

        @param force: Flag indicating whether the update is forced.
        @type force: C{boolean}

        @return: A deferred that fires when the operation completes.

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 user -i -f', results.errors)
                else:
                    raise CommandError('p4 user -i', results.errors)
        
        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'user', '-i', '-f',
                              input=self._form)
        else:
            d = maybeDeferred(self.__connection.run,
                              'user', '-i',
                              input=self._form)
        d.addCallback(handleResults)
        return d

    def delete(self, force=False):
        """Delete this user from the Perforce server.

        By default a user can only delete their own user specification.
        Specifying the C{force} parameter as C{True} allows users with
        C{'super'} access to delete other users.

        @param force: Flag indicating whether to force deletion of the user.
        @type force: C{boolean}

        @return: A deferred that fires when the operation completes.

        @raise CommandError: If the operation failed due to Perforce errors.
        """

        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 user -d -f %s' % self.__name,
                                       results.errors)
                else:
                    raise CommandError('p4 user -d %s' % self.__name,
                                       results.errors)

        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'user', '-d', '-f', self.__name)
        else:
            d = maybeDeferred(self.__connection.run,
                              'user', '-d', self.__name)
        d.addCallback(handleResults)
        return d

    def setPassword(self, newPassword, oldPassword=None):
        """Set a new password for this user.

        By default a user can only change their own password, and then only
        if they correctly provide their old password. However, users with
        'super' access can set new passwords for other users without providing
        the old password.

        @param newPassword: The new password to set.
        Pass None or '' for the new password to set it to blank.
        @type newPassword: C{str}, C{unicode} or C{None}

        @param oldPassword: The old password. Leave as C{None} to set someone
        else's password without the old password (provided you have 'super'
        access).
        @type oldPassword: C{str}, C{unicode} or C{None}

        @return: A deferred that fires when the operation completes.

        @raise CommandError: If the operation failed due to Perforce errors.
        """

        from twisted.internet.defer import maybeDeferred

        if newPassword is None:
            newPassword = ''

        if oldPassword is None or self.__name != self.__connection.user:

            def handleResults(results):
                if results.errors:
                    raise CommandError('p4 passwd %s' % self.__name,
                                       results.errors)
            
            # Setting a password without the old password or setting another
            # user's password needs 'super' access.
            d = maybeDeferred(self.__connection.run,
                              'passwd', self.__name,
                              input=[newPassword,
                                     newPassword])
            d.addCallback(handleResults)
            return d
        
        else:
            def handleResults(results):
                if results.errors:
                    raise CommandError('p4 passwd',
                                       results.errors)
            
            # Setting the current user's password
            if oldPassword == '':
                d = maybeDeferred(self.__connection.run,
                                  'passwd',
                                  input=[newPassword,
                                         newPassword])
            else:
                d = maybeDeferred(self.__connection.run,
                                  'passwd',
                                  input=[oldPassword,
                                         newPassword,
                                         newPassword])
            d.addCallback(handleResults)
            return d

class Branch(FormObject):
    """A Perforce branch object."""

    __slots__ = ["__connection", "__name"]

    def __new__(cls, connection, branchName):
        """Intialise the Branch based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must be already connected.
        @type connection: L{perforce.connection.Connection}

        @param branchName: The name of the branch to query.
        @type branchName: C{str} or C{unicode}

        @return: A deferred that fires with the L{Branch} object once the
        form has been retrieved.
        @rtype: L{Branch}

        @raise CommandError: If there was a Perforce error querying the branch.
        """
        def handleResults(results):
            if results.errors or not results.forms:
                raise CommandError('p4 branch -o %s' % branchName,
                                   results.messages)

            form = results.forms[0]
            self = object.__new__(cls)
            Branch.__init__(self, connection, branchName, form)
            return self

        from twisted.internet.defer import maybeDeferred
        d = maybeDeferred(connection.run, 'branch', '-o', branchName)
        d.addCallback(handleResults)
        return d

    def __init__(self, connection, branchName, form):
        """Intialise the Branch based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must be already connected.
        @type connection: L{perforce.connection.Connection}

        @param branchName: The name of the branch to query.
        @type branchName: C{str} or C{unicode}

        @param form: The form returned from the Perforce server.
        @type form: L{perforce.forms.Form}
        """
        FormObject.__init__(self, form)
        self.__connection = connection
        self.__name = branchName

    def save(self, force=False):
        """Save any changes made to the branch to the Perforce server.

        By default only the owner of a locked branch can modify the branch.
        Passing C{force} as C{True} allows users with C{'admin'} access to
        modify locked branches owned by another user.

        @param force: Flag indicating whether to force saving of updates.
        @type force: C{boolean}

        @return: A deferred that fires when the operation is complete.

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 branch -i -f', results.errors)
                else:
                    raise CommandError('p4 branch -i', results.errors)
            
        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'branch', '-i', '-f',
                              input=form)
        else:
            d = maybeDeferred(self.__connection.run,
                              'branch', '-i',
                              input=form)
        d.addCallback(handleResults)
        return d

    def delete(self, force=False):
        """Delete this branch from the Perforce server.

        By default, a branch cannot be deleted if it is locked.
        Specifying the 'force' parameter as True allows users with 'admin'
        access to delete locked branches.

        @param force: Flag indicating whether to force deletion of the branch.
        @type force: C{boolean}

        @return: A deferred that fires when the operation is complete.

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 branch -d -f %s' % self.__name,
                                       results.errors)
                else:
                    raise CommandError('p4 branch -d %s' % self.__name,
                                       results.errors)

        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'branch', '-d', '-f', self.__name)
        else:
            d = maybeDeferred(self.__connection.run,
                              'branch', '-d', self.__name)
        d.addCallback(handleResults)
        return d

class Label(FormObject):
    """The label class wraps the Perforce label concept."""

    __slots__ = ['__connection', '__name']

    def __new__(cls, connection, labelName):
        """Construct a Label based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must be already connected.
        @type connection: L{perforce.connection.Connection} or
        L{perforce.async.connection.Connection}

        @param labelName: The name of the label to query.
        @type labelName: C{str} or C{unicode}

        @return: A deferred that fires with a L{Label} object once the form
        has been retrieved.

        @raise CommandError: If there was a Perforce error querying the label.
        """ 
        def handleResults(results):
            if results.errors or not results.forms:
                raise CommandError('p4 label -o %s' % labelName,
                                   results.messages)

            form = results.forms[0]
            self = object.__new__(cls)
            Label.__init__(self, connection, labelName, form)
            return self

        from twisted.internet.defer import maybeDeferred
        d = maybeDeferred(connection.run, 'label', '-o', labelName)
        d.addCallback(handleResults)
        return d

    def __init__(self, connection, labelName, form):
        """Intialise the Label based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must be already connected.
        @type connection: L{perforce.connection.Connection}

        @param labelName: The name of the label to query.
        @type labelName: C{str} or C{unicode}

        @param form: The form retrieved from the Perforce server.
        @type form: L{perforce.forms.Form}
        """
        FormObject.__init__(self, form)
        self.__connection = connection
        self.__name = labelName

    def save(self, force=False):
        """Save any changes made to the label on the Perforce server.

        By default a locked label can only be updated by its owner. Passing
        C{force} as C{True} will allow users with C{'admin'} access to force
        saving changes to the labe.

        @param force: Flag indicating whether to force saving of updates.
        @type force: C{boolean}

        @return: A deferred that fires when the operation completes.
        
        @raise CommandError: If the operation failed due to Perforce errors.
        """
        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 label -i -f', results.errors)
                else:
                    raise CommandError('p4 label -i', results.errors)
        
        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'label', '-i', '-f',
                              input=self._form)
        else:
            d = maybeDeferred(self.__connection.run,
                              'label', '-i',
                              input=self._form)
        d.addCallback(handleResults)
        return d

    def delete(self, force=False):
        """Delete this label from the Perforce server.

        By default a locked label can't be deleted. Users with 'admin' access
        can force deletion of a locked label by specifying C{force} as C{True}.

        @param force: Flag indicating whether to force deletion of a locked
        label.
        @type force: C{boolean}

        @return: A deferred that fires when the operation completes.

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 user -d -f %s' % self.__name,
                                       results.errors)
                else:
                    raise CommandError('p4 user -d %s' % self.__name,
                                       results.errors)
        
        from twisted.internet.defer import maybeDeferred
        if force:
            d = maybeDeferred(self.__connection.run,
                              'label', '-d', '-f', self.__name)
        else:
            d = maybeDeferred(self.__connection.run,
                              'label', '-d', self.__name)
        d.addCallback(handleResults)
        return d

class Change(FormObject):
    """The change class wraps the Perforce changelist concept."""

    __slots__ = ['__connection', '__name', '__client']

    __changeCreatedMessageRE = re.compile(
        '^Change (?P<change>\d+) created')
    __changeRenamedMessageRE = re.compile(
        '^Change (?P<old>\d+) renamed change (?P<new>\d+)')

    def __new__(cls, connection, change=None, client=None):
        """Initialise the Change based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must already be connected.
        @type connection: L{perforce.connection.Connection} or
        L{perforce.async.connection.Connection}

        @param change: The number of the changelist to retrieve.
        If not specified then open the default changelist on the connection's
        current client. Saving the default changelist will create a new named
        changelist.
        @type change: C{int}, C{str}, C{unicode} or C{None}

        @param client: The name of the Perforce client to use for retrieving
        default changelists and submitting files. The client used to submit
        the changelist must be the same as the client the changelist was
        created on.
        @type client: C{str} or C{unicode}

        @return: A deferred that fires with a L{Change} object once the form
        has been retrieved.

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        def handleResults(results):
            if results.errors or not results.forms:
                if change is None:
                    raise CommandError('p4 change -o',
                                       results.messages)
                else:
                    raise CommandError('p4 change -o %s' % str(change),
                                       results.messages)

            form = results.forms[0]
            self = object.__new__(cls)
            Change.__init__(self, connection, change, client, form)
            return self

        from twisted.internet.defer import maybeDeferred
        if change is None:
            d = maybeDeferred(connection.run, 'change', '-o',
                              client=client or connection.client)
        else:
            d = maybeDeferred(connection.run, 'change', '-o', str(change),
                              client=client or connection.client)
        d.addCallback(handleResults)
        return d

    def __init__(self, connection, change, client, form):
        """Initialise the Change based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must already be connected.
        @type connection: L{perforce.connection.Connection} or
        L{perforce.async.connection.Connection}

        @param change: The number of the changelist to retrieve.
        If not specified then open the default changelist on the connection's
        current client. Saving the default changelist will create a new named
        changelist.
        @type change: C{int}, C{str}, C{unicode} or C{None}

        @param client: The name of the Perforce client to use for retrieving
        default changelists and submitting files. The client used to submit
        the changelist must be the same as the client the changelist was
        created on.
        @type client: C{str}, C{unicode}

        @param form: The form retrieved from the Perforce server.
        @type form: L{perforce.forms.Form}
        """
        FormObject.__init__(self, form)
        
        self.__connection = connection
        self.__client = client
        
        if change is None:
            self.__name = None
        else:
            self.__name = str(change)

    def save(self, force=False):
        """Save any changes made to the changelist on the Perforce server.

        @param force: Flag indicating whether or not to force update of other
        users' pending changelists or 'Update' and 'Description' fields of
        submitted changelists. The user must have 'admin' privileges to
        force modification of changelists.
        @type force: C{boolean}

        @return: A deferred that fires when the operation is complete.

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        def handleResults(results):
            if results.errors:
                if force:
                    raise CommandError('p4 change -s -f -i',
                                       results.errors)
                else:
                    raise CommandError('p4 change -s -i',
                                       results.errors)

            if self.__name is None:
                # We just saved a new change form, query the new change number.
                message = results.infos[0].format()
                match = Change.__changeCreatedMessageRE.match(message)
                if not match:
                    raise RuntimeError(
                        "Perforce server returned an unrecognised response " +
                        "creating a new changelist: %s" % message)

                self.__name = match.group('change')

        from twisted.internet.defer import maybeDeferred

        client = self.__client or self.__connection.client
        if force:
            d = maybeDeferred(self.__connection.run,
                              'change', '-s', '-f', '-i',
                              intput=self._form,
                              client=client)
        else:
            d = maybeDeferred(self.__connection.run,
                              'change', '-s', '-i',
                              input=self._form,
                              client=client)
        d.addCallback(handleResults)
        return d

    def delete(self, force=False):
        """Delete a pending changelist on the Perforce server.

        @note: The default changelist cannot be deleted.

        @param force: Force deletion of another user's changelist or a
        submitted changelist (once all files on the changelist have been
        obliterated). The user must have 'admin' privileges to force
        deletion of changelists.
        @type force: C{boolean}

        @raise CommandError: If the operation failed due to Perforce errors.
        """

        client = self.__client or self.__connection.client
        if force:
            results = self.__connection.run('change', '-d', '-f', self.__name,
                                            client=client)
            if results.errors:
                raise CommandError('p4 change -d -f %s' % self.__name,
                                   results.errors)
        else:
            results = self.__connection.run('change', '-d', self.__name,
                                            client=client)
            if results.errors:
                raise CommandError('p4 change -d %s' % self.__name,
                                   results.errors)

    def submit(self):
        """Save any changes made to the changelist and submit the changelist to
        the Perforce server.

        This will atomically commit changes to files associated with this
        changelist.

        @return: A deferred that fires when the operation is complete.

        @raise CommandError: If the operation fails due to Perforce errors.
        """

        def performSubmit(dummy):

            assert self.__name is not None

            client = self.__client or self.__connection.client
            
            from twisted.internet.defer import maybeDeferred
            d = maybeDeferred(self.__connection.run,
                              'submit', '-s', '-c', self.__name,
                              client=client)
            d.addCallback(handleResults)
            return d

        def handleResults(results):
            if results.errors:
                raise CommandError('p4 submit -s -c %s' % self.__name,
                                   results.errors)
                
            # The changelist may have been renamed to a different number
            # upon submission, check to see what that number is.
            if int(self.__connection.server) < 20 or \
                   float(perforce.api.version) < 2005.2:
                # Pre 2005.2 has no tagged output
                
                # Check the last info message for a
                # 'Change x renamed change y' message.
                msg = results.infos[-1].format()
                match = Change.__changeRenamedMessageRE.match(msg)
                if match:
                    assert match.group('old') == self.__name
                    self.__name = match.group('new')
            else:
                # 2005.2 or later has tagged output for 'p4 submit'
                self.__name = results.records[-1]['submittedChange']

        # Save any changes first
        #
        # This simplifies the process of handling a failed submission of the
        # default changelist as the 'p4 submit -i' call would implicitly
        # creates a named changelist and then run 'p4 submit -c <num>'.
        # So we may as well just do that ourselves and keep the logic for
        # querying the name of newly created changes in the save() method.
        #
        # This means that if the save operation succeeds but the submit
        # fails, the Change object will still be updated with the new change
        # number.
        d = self.save()
        d.addCallback(performSubmit)
        return d

    def refresh(self):
        """Reload the changelist contents from the Perforce server, discarding
        any unsaved changes.

        @return: A deferred that fires when the operation is complete.

        @raise CommandError: If the operation fails due to Perforce errors.
        """

        def handleResults(results):
            if results.errors:
                if self.__name is None:
                    raise CommandError('p4 change -s -o',
                                       results.errors)
                else:
                    raise CommandError('p4 change -s -o %s' % self.__name,
                                       results.errors)

            # Update the form object
            self._form = results.forms[0]

        from twisted.internet.defer import maybeDeferred

        client = self.__client or self.__connection.client
        if self.__name is None:
            # Retrieve the default changelist
            d = maybeDeferred(self.__connection.run,
                              'change', '-s', '-o',
                              client=client)
        else:
            # Retrieve the named changelist
            d = maybeDeferred(self.__connection.run,
                              'change', '-s', '-o', self.__name,
                              client=client)
        d.addCallback(handleResults)
        return d
