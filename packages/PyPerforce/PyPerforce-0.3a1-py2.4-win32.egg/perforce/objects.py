"""Object-oriented interfaces for Perforce entities."""

__all__ = ['CommandError',
           'Client', 'User', 'Branch', 'Label', 'Change']

import re
import perforce.api

class CommandError(perforce.api.PerforceError):
    """Exception raised when a Perforce command fails."""
    
    def __init__(self, command, errors):
        self.command = command
        self.errors = errors

    def __str__(self):
        return "\n".join((x.format() for x in self.errors))

class FormObject(object):
    """A Perforce form-based object.

    Provides dictionary-style index access to form fields and to 'Options'
    field values.

    For example::
      | >>> c = FormObject(clientForm)
      | >>> print c['Options']
      | noallwrite noclobber nocompress unlocked nomodtime normdir
      | >>> print c['compress']
      | False
      | >>> c['compress'] = True
      | >>> print c['Options']
      | noallwrite noclobber compress unlocked nomodtime normdir
      | >>> print c['compress']
      | True
    """

    __slots__ = ['_form']

    def __init__(self, form):
        self._form = form

    def __getitem__(self, key):
        if key in self._form:
            return self._form[key]            
        elif 'Options' in self._form:
            field = self._form.Options
            if field.isSingle() and field.values is not None:
                fieldValues = field.values
                if not isinstance(fieldValues, list):
                    fieldValues = [fieldValues]
                vals = self._form['Options'].split()
                for opts in fieldValues:
                    if key in opts:
                        return key in vals
        raise KeyError("No such field or option '%s'" % key)          

    def __setitem__(self, key, value):
        if key in self._form:
            self._form[key] = value
            return
        elif 'Options' in self._form:
            field = self._form.Options
            if field.isSingle() and field.values is not None:
                fieldValues = field.values
                if not isinstance(fieldValues, list):
                    fieldValues = [fieldValues]
                vals = self._form['Options'].split()
                for opts in fieldValues:
                    if key in opts:
                        others = [opt for opt in opts if opt != key]
                        if value:
                            # Set to true by replacing one of the other values
                            # with this value or adding it to the list.
                            for other in others:
                                if other in vals:
                                    vals[vals.index(other)] = key
                                    break
                            else:
                                if key not in vals:
                                    vals.append(key)
                        else:
                            # Set to false by replacing this one with the other
                            # value or appending the other value to the list.
                            if len(others) != 1:
                                raise KeyError(
                                    ("Ambiguous operation setting option '%s'"+
                                     "to False") % key)
                            
                            if key in vals:
                                vals[vals.index(key)] = others[0]
                            elif others[0] not in vals:
                                vals.append(others[0])
                        self._form['Options'] = ' '.join(vals)
                        return
        raise KeyError("No such field or option '%s'" % key)

    def __delitem__(self, key):
        del self._form[key]

class Client(FormObject):
    """A Perforce client/workspace object."""

    __slots__ = ['__connection', '__name']

    def __init__(self, connection, clientName):
        """Initialises the Client based on the form retrieved on the
        connection.

        @param connection: The connection to the Perforce server to use to
        query the client details.
        @type connection: L{perforce.connection.Connection}

        @param clientName: The name of the Perforce client to query.
        @type clientName: C{str} or C{unicode}

        @raise CommandError: If there was a Perforce error querying the client.
        """
        results = connection.run('client', '-o', clientName)
        if results.errors or not results.forms:
            raise CommandError('p4 client -o %s' % clientName,
                               results.messages)
        
        form = results.forms[0]
        
        FormObject.__init__(self, form)
        self.__connection = connection
        self.__name = clientName

    def save(self):
        """Save any changes made to the client on the Perforce server.

        @raise CommandError: If there was a Perforce error saving the client.
        """
        results = self.__connection.run('client', '-i', input=self._form)
        if results.errors:
            raise CommandError('p4 client -i', results.errors)

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

        @return: The results of performing the sync operation
        @rtype: L{perforce.results.Results}

        @raise CommandError: If there was a Perforce error syncing the client.
        """
        force = False
        if 'force' in options:
            force = options['force']

        overrides = {'client' : self.__name}
        if force:
            results = self.__connection.run('sync', '-f',
                                            *fileRevisions,
                                            **overrides)
        else:
            results = self.__connection.run('sync',
                                            *fileRevisions,
                                            **overrides)
        return results

    def delete(self, force=False):
        """Delete this client workspace from the Perforce repository.

        The client cannot normally be deleted when the client is locked.
        Passing force=True will allow the client owner or a Perforce user with
        admin privileges to forcibly delete a locked client.

        @note: This operation will not delete the files from the client's
        directory.

        @raise CommandError: If there was a Perforce error deleting the client.
        """
        if force:
            results = self.__connection.run('client', '-d', '-f', self.__name)
        else:
            results = self.__connection.run('client', '-d', self.__name)

        if results.errors:
            if force:
                raise CommandError('p4 client -d -f %s' % self.__name,
                                   results.errors)
            else:
                raise CommandError('p4 client -d %s' % self.__name,
                                   results.errors)

class User(FormObject):
    """A Perforce user object."""

    __slots__ = ['__connection', '__name']

    def __init__(self, connection, userName):
        """Initialises the User based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        @type connection: L{perforce.connection.Connection}

        @param userName: The name of the user to query.
        @type userName: C{str} or C{unicode}

        @raise CommandError: If there was a Perforce error querying the user.
        """
        results = connection.run('user', '-o', userName)
        if results.errors or not results.forms:
            raise CommandError('p4 user -o %s' % userName,
                               results.messages)
        form = results.forms[0]
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

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        if force:
            results = self.__connection.run('user', '-i', '-f',
                                            input=self._form)
        else:
            results = self.__connection.run('user', '-i',
                                            input=self._form)
            
        if results.errors:
            if force:
                raise CommandError('p4 user -i -f', results.errors)
            else:
                raise CommandError('p4 user -i', results.errors)

    def delete(self, force=False):
        """Delete this user from the Perforce server.

        By default a user can only delete their own user specification.
        Specifying the C{force} parameter as C{True} allows users with
        C{'super'} access to delete other users.

        @param force: Flag indicating whether to force deletion of the user.
        @type force: C{boolean}

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        if force:
            results = self.__connection.run('user', '-d', '-f', self.__name)
        else:
            results = self.__connection.run('user', '-d', self.__name)

        if results.errors:
            if force:
                raise CommandError('p4 user -d -f %s' % self.__name,
                                   results.errors)
            else:
                raise CommandError('p4 user -d %s' % self.__name,
                                   results.errors)

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

        @raise CommandError: If the operation failed due to Perforce errors.
        """

        if newPassword is None:
            newPassword = ''

        if oldPassword is None or self.__name != self.__connection.user:
            # Setting a password without the old password or setting another
            # user's password needs 'super' access.
            results = self.__connection.run('passwd', self.__name,
                                            input=[newPassword,
                                                   newPassword])
            if results.errors:
                raise CommandError('p4 passwd %s' % self.__name,
                                   results.errors)
        else:
            # Setting the current user's password
            if oldPassword == '':
                results = self.__connection.run('passwd',
                                                input=[newPassword,
                                                       newPassword])
            else:
                results = self.__connection.run('passwd',
                                                input=[oldPassword,
                                                       newPassword,
                                                       newPassword])
                
            if results.errors:
                raise CommandError('p4 passwd',
                                   results.errors)

class Branch(FormObject):
    """A Perforce branch object."""

    __slots__ = ["__connection", "__name"]

    def __init__(self, connection, branchName):
        """Intialise the Branch based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must be already connected.
        @type connection: L{perforce.connection.Connection}

        @param branchName: The name of the branch to query.
        @type branchName: C{str} or C{unicode}

        @raise CommandError: If there was a Perforc error querying the branch.
        """
        results = connection.run('branch', '-o', branchName)
        if results.errors:
            raise CommandError('p4 branch -o %s' % branchName,
                               results.errors)
        form = results.forms[0]
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

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        form = self._form
        if force:
            results = self.__connection.run('branch', '-i', '-f',
                                            input=form)
            if results.errors:
                raise CommandError('p4 branch -i -f', results.errors)
        else:
            results = self.__connection.run('branch', '-i',
                                            input=form)
            if results.errors:
                raise CommandError('p4 branch -i', results.errors)

    def delete(self, force=False):
        """Delete this branch from the Perforce server.

        By default, a branch cannot be deleted if it is locked.
        Specifying the 'force' parameter as True allows users with 'admin'
        access to delete locked branches.

        @param force: Flag indicating whether to force deletion of the branch.
        @type force: C{boolean}

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        if force:
            results = self.__connection.run('branch', '-d', '-f', self.__name)
            if results.errors:
                raise CommandError('p4 branch -d -f %s' % self.__name,
                                   results.errors)
        else:
            results = self.__connection.run('branch', '-d', self.__name)
            if results.errors:
                raise CommandError('p4 branch -d %s' % self.__name,
                                   results.errors)

class Label(FormObject):
    """The label class wraps the Perforce label concept."""

    __slots__ = ['__connection', '__name']

    def __init__(self, connection, labelName):
        """Intialise the Label based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must be already connected.
        @type connection: L{perforce.connection.Connection}

        @param labelName: The name of the label to query.
        @type labelName: C{str} or C{unicode}

        @raise CommandError: If there was a Perforce error querying the label.
        """
        results = connection.run('label', '-o', labelName)
        if results.errors:
            raise CommandError('p4 label -o %s' % labelName,
                               results.errors)
        form = results.forms[0]
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
        
        @raise CommandError: If the operation failed due to Perforce errors.
        """
        if force:
            results = self.__connection.run('label', '-i', '-f',
                                            input=self._form)
        else:
            results = self.__connection.run('label', '-i',
                                            input=self._form)

        if results.errors:
            if force:
                raise CommandError('p4 label -i -f', results.errors)
            else:
                raise CommandError('p4 label -i', results.errors)

    def delete(self, force=False):
        """Delete this label from the Perforce server.

        By default a locked label can't be deleted. Users with 'admin' access
        can force deletion of a locked label by specifying C{force} as C{True}.

        @param force: Flag indicating whether to force deletion of a locked
        label.
        @type force: C{boolean}

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        if force:
            results = self.__connection.run('label', '-d', '-f', self.__name)
        else:
            results = self.__connection.run('label', '-d', self.__name)

        if results.errors:
            if force:
                raise CommandError('p4 user -d -f %s' % self.__name,
                                   results.errors)
            else:
                raise CommandError('p4 user -d %s' % self.__name,
                                   results.errors)

class Change(FormObject):
    """The change class wraps the Perforce changelist concept."""

    __slots__ = ['__connection', '__name', '__client']

    __changeCreatedMessageRE = re.compile(
        '^Change (?P<change>\d+) created')
    __changeRenamedMessageRE = re.compile(
        '^Change (?P<old>\d+) renamed change (?P<new>\d+)')

    def __init__(self, connection, change=None, client=None):
        """Initialise the Change based on the form retrieved on the connection.

        @param connection: The connection to the Perforce server to use.
        Must already be connected.
        @type connection: L{perforce.connection.Connection}

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

        @raise CommandError: If the operation failed due to Perforce errors.
        """
        FormObject.__init__(self, None)
        
        self.__connection = connection
        self.__client = client
        
        if change is None:
            self.__name = None
        elif isinstance(change, int):
            self.__name = str(change)
        elif isinstance(change, basestring):
            self.__name = change
        else:
            raise TypeError("Invalid type for 'change' parameter.")
            
        self.refresh()

    def save(self, force=False):
        """Save any changes made to the changelist on the Perforce server.

        @param force: Flag indicating whether or not to force update of other
        users' pending changelists or 'Update' and 'Description' fields of
        submitted changelists. The user must have 'admin' privileges to
        force modification of changelists.
        @type force: C{boolean}

        @raise CommandError: If the operation failed due to Perforce errors.
        """

        client = self.__client or self.__connection.client
        if force:
            results = self.__connection.run('change', '-s', '-f', '-i',
                                            intput=self._form,
                                            client=client)
            if results.errors:
                raise CommandError('p4 change -s -f -i',
                                   results.errors)
        else:
            results = self.__connection.run('change', '-s', '-i',
                                            input=self._form,
                                            client=client)
            if results.errors:
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

        @raise CommandError: If the operation fails due to Perforce errors.
        """

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
        self.save()

        assert self.__name is not None

        client = self.__client or self.__connection.client
        results = self.__connection.run('submit', '-s', '-c', self.__name,
                                        client=client)
        
        if results.errors:
            raise CommandError('p4 submit -s -c %s' % self.__name,
                               results.errors)

        # The changelist may have been renamed to a different number upon
        # submission, check to see what that number is.
        if int(self.__connection.server) < 20 or \
           float(perforce.api.version) < 2005.2:
            # Pre 2005.2 has no tagged output

            # Check the last info message for a 'Change x renamed change y'
            # message.
            msg = results.infos[-1].format()
            match = Change.__changeRenamedMessageRE.match(msg)
            if match:
                assert match.group('old') == self.__name
                self.__name = match.group('new')
        else:
            # 2005.2 or later has tagged output for 'p4 submit'
            self.__name = results.records[-1]['submittedChange']

    def refresh(self):
        """Reload the changelist contents from the Perforce server, discarding
        any unsaved changes.

        @raise CommandError: If the operation fails due to Perforce errors.
        """

        client = self.__client or self.__connection.client
        if self.__name is None:
            # Retrieve the default changelist
            results = self.__connection.run('change', '-s', '-o',
                                            client=client)
            if results.errors:
                raise CommandError('p4 change -s -o',
                                   results.errors)
        else:
            # Retrieve the named changelist
            results = self.__connection.run('change', '-s', '-o', self.__name,
                                            client=client)
            if results.errors:
                raise CommandError('p4 change -s -o %s' % self.__name,
                                   results.errors)

        # Update the form object
        self._form = results.forms[0]

class Counter(object):
    """A named Perforce counter value.

    A Perforce counter is a named integer value stored on the Perforce
    server. Counters that haven't previously been set all have an
    initial value of zero.

    Reading the value of a counter requires 'list' permissions.
    Modifying the value of a counter requires 'review' permissions.
    Modifying a protected counter requires 'super' permissions.

    @warning: Counter value manipulation does not support atomic operations
    and so it is recommended that only a single process attempts to modify
    a particular counter.
    """

    __slots__ = ['__connection', '__name']

    def __init__(self, connection, name):
        """Construct a named counter object.

        @param connection: The connection to the Perforce server to use.
        @type connection: L{perforce.connection.Connection}

        @param name: The name of the counter.
        @type name: C{str} or C{unicode}
        """
        self.__connection = connection
        self.__name = name

    @property
    def name(self):
        """The name of the counter.

        @type: C{str} or C{unicode}
        """
        return self.__name

    def getValue(self):
        """Retrieve the current value of the counter.

        @note: Requires 'list' access permissions.

        @return: The value of the counter.
        @rtype: C{int}
        """
        
        results = self.__connection.run('counter', self.__name)
        if results.errors:
            raise CommandError('p4 counter %s' % self.__name,
                               results.messages)

        if results.records:
            return int(results.records[0]['value'])
        else:
            return int(results.infos[0].format())

    def setValue(self, value, force=False):
        """Set a new value for the counter.

        @note: Requires 'review' access permissions.

        @param value: The new value to set the counter to.
        @type value: C{str}, C{unicode} or C{int}

        @param force: If C{True}, force setting of a protected Perforce
        counter such as 'job', 'change' or 'security'.
        Otherwise an error will be raised.
        Requires 'super' access permissions.
        @type force: C{boolean}

        @raise CommandError: If the counter could not be set.
        eg. due to insufficient permissions.
        """
        value = str(int(value))
        if force:
            results = self.__connection.run('counter', '-f',
                                            self.__name, str(value))
            if results.errors:
                raise CommandError('p4 counter -f %s %s' % (self.__name,
                                                            str(value)),
                                   results.errors)
        else:
            results = self.__connection.run('counter',
                                            self.__name, str(value))
            if results.errors:
                raise CommandError('p4 counter %s %s' % (self.__name,
                                                         str(value)),
                                   results.errors)
