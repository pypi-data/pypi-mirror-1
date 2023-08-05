"""perforce.tests.forms - Unit tests for the perforce.forms module classes."""

import unittest

import perforce.forms

class FormTests(unittest.TestCase):

    def testUserForm(self):

        specdef = "".join(
            ["User;code:651;rq;ro;seq:1;len:32;;",
             "Email;code:652;fmt:R;rq;seq:3;len:32;;",
             "Update;code:653;fmt:L;type:date;ro;seq:2;len:20;;",
             "Access;code:654;fmt:L;type:date;ro;len:20;;",
             "FullName;code:655;fmt:R;type:line;rq;len:32;;",
             "JobView;code:656;type:line;len:64;;",
             "Password;code:657;len:32;;",
             "Reviews;code:658;type:wlist;len:64;;"])

        data = """
# A Perforce User Specification.
#
#  User:        The user's user name.
#  Email:       The user's email address; for email review.
#  Update:      The date this specification was last modified.
#  Access:      The date this user was last active.  Read only.
#  FullName:    The user's real name.
#  JobView:     Selects jobs for inclusion during changelist creation.
#  Password:    If set, user must have matching $P4PASSWD on client.
#  Reviews:     Listing of depot files to be reviewed by user.

User:   test

Email:  test@somecompany.com

Update: 2000/01/01 12:00:00

Access: 2001/01/01 12:00:00

FullName:       Joe Tester

JobView:        user=test&status=open

Reviews:
        //depot/...
"""
        
        form = perforce.forms.Form(specdef, data)

        self.assertEqual(len(form), 8)
        for field in ['User', 'Email', 'Update', 'Access',
                      'FullName', 'JobView', 'Password', 'Reviews']:
            self.failUnless(field in form)

        for field in form:
            self.failUnless(field in ['User', 'Email', 'Update', 'Access',
                                      'FullName', 'JobView', 'Password',
                                      'Reviews'])

        self.assertEqual(form['User'], "test")
        self.assertEqual(form['Email'], "test@somecompany.com")
        self.assertEqual(form['Update'], "2000/01/01 12:00:00")
        self.assertEqual(form['Access'], "2001/01/01 12:00:00")
        self.assertEqual(form['FullName'], "Joe Tester")
        self.assertEqual(form['JobView'], "user=test&status=open")
        self.assertEqual(form['Reviews'], ["//depot/..."])
        self.assertEqual(form['Password'], None)

        # Make some changes
        form['Password'] = "secret"
        form['Reviews'] = ["//depot/joe/...",
                           "//depot/main/..."]
        form['JobView'] = None
        form['Email'] = "joe@foo.bar"

        # Format and parse the updated form
        newData = str(form)
        newForm = perforce.forms.Form(specdef, newData)

        self.assertEqual(newForm['User'], "test")
        self.assertEqual(newForm['Email'], "joe@foo.bar")
        self.assertEqual(newForm['Update'], "2000/01/01 12:00:00")
        self.assertEqual(newForm['Access'], "2001/01/01 12:00:00")
        self.assertEqual(newForm['FullName'], "Joe Tester")
        self.assertEqual(newForm['JobView'], None)
        self.assertEqual(newForm['Reviews'], ["//depot/joe/...",
                                              "//depot/main/..."])
        self.assertEqual(newForm['Password'], "secret")

    def testUnicodeUserForm(self):

        specdef = u"".join(
            [u"User;code:651;rq;ro;seq:1;len:32;;",
             u"Email;code:652;fmt:R;rq;seq:3;len:32;;",
             u"Update;code:653;fmt:L;type:date;ro;seq:2;len:20;;",
             u"Access;code:654;fmt:L;type:date;ro;len:20;;",
             u"FullName;code:655;fmt:R;type:line;rq;len:32;;",
             u"JobView;code:656;type:line;len:64;;",
             u"Password;code:657;len:32;;",
             u"Reviews;code:658;type:wlist;len:64;;"])

        data = u"""
# A Perforce User Specification.
#
#  User:        The user's user name.
#  Email:       The user's email address; for email review.
#  Update:      The date this specification was last modified.
#  Access:      The date this user was last active.  Read only.
#  FullName:    The user's real name.
#  JobView:     Selects jobs for inclusion during changelist creation.
#  Password:    If set, user must have matching $P4PASSWD on client.
#  Reviews:     Listing of depot files to be reviewed by user.

User:   test

Email:  test@somecompany.com

Update: 2000/01/01 12:00:00

Access: 2001/01/01 12:00:00

FullName:       Joe Tester

JobView:        user=test&status=open

Reviews:
        //depot/...
"""
        
        form = perforce.forms.Form(specdef, data)

        self.assertEqual(len(form), 8)
        for field in ['User', 'Email', 'Update', 'Access',
                      'FullName', 'JobView', 'Password', 'Reviews']:
            self.failUnless(field in form)

        for field in form:
            self.failUnless(field in ['User', 'Email', 'Update', 'Access',
                                      'FullName', 'JobView', 'Password',
                                      'Reviews'])

        self.assertEqual(form['User'], "test")
        self.assertEqual(form['Email'], "test@somecompany.com")
        self.assertEqual(form['Update'], "2000/01/01 12:00:00")
        self.assertEqual(form['Access'], "2001/01/01 12:00:00")
        self.assertEqual(form['FullName'], "Joe Tester")
        self.assertEqual(form['JobView'], "user=test&status=open")
        self.assertEqual(form['Reviews'], ["//depot/..."])
        self.assertEqual(form['Password'], None)

        # Make some changes
        form['Password'] = "secret"
        form['Reviews'] = ["//depot/joe/...",
                           "//depot/main/..."]
        form['JobView'] = None
        form['Email'] = "joe@foo.bar"

        # Format and parse the updated form
        newData = str(form)
        newForm = perforce.forms.Form(specdef, newData)

        self.assertEqual(newForm['User'], "test")
        self.assertEqual(newForm['Email'], "joe@foo.bar")
        self.assertEqual(newForm['Update'], "2000/01/01 12:00:00")
        self.assertEqual(newForm['Access'], "2001/01/01 12:00:00")
        self.assertEqual(newForm['FullName'], "Joe Tester")
        self.assertEqual(newForm['JobView'], None)
        self.assertEqual(newForm['Reviews'], ["//depot/joe/...",
                                              "//depot/main/..."])
        self.assertEqual(newForm['Password'], "secret")
