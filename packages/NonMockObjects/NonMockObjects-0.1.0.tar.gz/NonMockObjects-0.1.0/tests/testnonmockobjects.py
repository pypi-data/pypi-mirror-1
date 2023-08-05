# --------------------------------------------------------------
#
# There's something nicely recursive about testing a test environment.

import unittest
import itertools
incrementer = itertools.count()

import sys
import os
if __name__ != "__main__":
    f = __file__
    f = os.path.normpath(os.path.dirname(f) + os.sep + os.pardir)
    if f not in sys.path: sys.path.append(f + os.sep + "src")
else:
    if os.pardir not in sys.path:
        sys.path.append(os.pardir + os.sep + "src")

from nonmockobjects import *


class Permission(object):
    Permissions = {}
    """This test class implements a permission, identified by a
    string. This is what I call an 'instance singleton' class; the
    class itself is not a singleton, but each value is."""

    def __new__(cls, name):
        try:
            return Permission.Permissions[name]
        except KeyError:
            pass

        permission = super(Permission, cls).__new__(cls)
        permission.name = name
        Permission.Permissions[name] = permission
        return permission

    # Hash on IDs
    def __eq__(self, other):
        return self is other
    def __hash__(self):
        return hash(self.name)
    def __repr__(self):
        return "<Permission: %s>" % self.name

@register
def permission(data, name = lambda: "testpermission%s" % incrementer.next()):
    return Permission(name)

@register
def permissionFromObjects(data):
    return Permission(data.permissionName)

@register
def permissionAllArgs(data, name = "moo"):
    return Permission(**all_args())

class User(object):
    """A user has some set of permissions. Empty permissions are
    invalid, an artificial constraint in this case but representing
    generally the creation-order constraints that commonly appear in
    the real world."""
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions

        if not self.permissions:
            raise ValueError("Must have some permissions to be a "
                             "user.")

    def __repr__(self):
        return "<User: %s>" % self.name

    @register_as('user')
    # Is there any way to avoid an explicit use of MergeCreate?
    def newUser(data, name = 'testuser%(inc)s', permission = permission):
        return User(name, [permission])
            
class Account(object):
    """An account has some set of users."""
    def __init__(self, name, users):
        self.name = name
        self.users = users

        if not self.users:
            raise ValueError("Must have some users to be an account.")

    def addUser(self, user):
        # In a real app, this might verify a user can't be added twice
        # or something else nice and complicated.
        self.users.append(user)

@register
def account(data, name = 'testaccount%(inc)s', user = User.newUser):
    return Account(name, [user])

@register
def addUserToAccount(data, account, user = User.newUser):
    account.addUser(user)
    return user

class Resources(object):
    def __init__(self, name, account):
        self.name = name
        self.account = account

        if not account:
            raise ValueError("Resources must belong to an account.")

class ObjectsTests(unittest.TestCase):
    def testFunctionality(self):
        """TestObjects works as expected"""
        data = Objects()
        permission = data.permission()
        self.assert_(permission.__class__ is Permission)
        self.assertEquals(permission.name[0:14], 'testpermission')

        permission2 = data.permission(name='cheese')
        self.assertEqual(permission2.name, 'cheese')

        permission3 = data.permission('cheese2')
        self.assertEqual(permission3.name, 'cheese2')
        
        user = data.user()
        self.assert_(user)
        self.assert_(user.permissions)
        self.assert_(len(user.permissions) == 1)
        # Is a new permission
        self.assert_(user.permissions[0] not in (permission,
                                                 permission2))

        user2 = data.user(permission=permission)
        self.assert_(len(user2.permissions) == 1)
        # Correctly used the given permission
        self.assertEqual(user2.permissions[0], permission)

        user3 = data.user(use_permission={'name': 'cheese2'})
        # Correctly took the argument.
        self.assertEqual(user3.permissions[0].name, 'cheese2')

        account = data.account()
        self.assert_(account)
        self.assert_(account.users[0])
        account = data.account(user=user)
        self.assert_(account.users[0] == user)

        # Test the recursion ability
        account = data.account(use_user={'permission': permission})
        self.assert_(account.users[0].permissions[0] == permission)
        account = data.account(use_user=
                                  {'use_permission':
                                   {'name': 'moogle'}})
        self.assert_(account.users[0].permissions[0].name == 'moogle')

        # Test the add-like functionality
        account = data.account()
        self.assertEqual(len(account.users), 1)
        user4 = data.addUserToAccount(account=account)
        self.assertEqual(len(account.users), 2)
        user4 = data.addUserToAccount(account, user=user2)
        self.assertEqual(len(account.users), 3)
        self.assertEqual(account.users[-1], user2)
        self.assertEqual(user2, user4)

        # Recursively specify that the new user must have a certain
        # permission
        user5 = data.addUserToAccount(account,
                                      use_user={'use_permission':
                                               {'name': 'reallynew'}})
        self.assertEqual(user5, account.users[-1])
        self.assertEqual(user5.permissions[0].name, 'reallynew')

        def takesArgs(*args): pass
        def takesKwargs(**kwargs): pass

        self.assertRaises(ValueError, register, takesArgs)
        self.assertRaises(ValueError, register, takesKwargs)

        data2 = Objects(permissionName = "datatest")
        permission = data2.permissionFromObjects()
        self.assertEquals(permission.name, 'datatest')

        permission = data.permissionAllArgs()
        self.assertEquals(permission.name, 'moo')
        permission = data.permissionAllArgs('moo2')
        self.assertEquals(permission.name, 'moo2')
        permission = data.permissionAllArgs(name = 'moo3')
        self.assertEquals(permission.name, 'moo3')

        def test(a, b, c):
            return all_args("b")

        self.assertEquals(test(1, 2, 3), {'c': 3})
        
if __name__ == "__main__":
    unittest.main()
