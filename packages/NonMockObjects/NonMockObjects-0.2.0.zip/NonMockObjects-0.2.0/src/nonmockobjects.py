"""
Summary
=======
 B{How to tell if you need this module}: You want to run automated
 tests on your code, but you have a relatively complicated data model,
 perhaps a nicely normalized database. The bulk of your tests consist
 of setting up this relatively complicated data model, and the tests
 all break whenever you change your model. Constructing the data has
 become so difficult (and breaks so often) that you've just stopped
 testing entirely.

 nonmockobjects.py is a framework I built to solve this problem. Some
 test systems seem to provide some limited support for very simple
 homogenous test data, like some small set of rows in one table,
 unrelated to anything else; this module is designed for the rapid
 creation of I{hierarchial, heterogenous} (or even graph-oriented)
 data at the relevant level of detail for your current test, without
 sacrificing the power to reach down four layers and set a certain
 setting for your test, and avoiding "mock objects" to the extent
 possible in favor of real objects.

 Example Of The Problem
 ----------------------

  Suppose we have a standard database application which includes Users,
  Accounts, Permissions, and Resources. For simplicity, suppose
  Permissions belong to Users, and Users and Resources belong to Accounts.

  Suppose the following constraints must hold, and are all tested upon
  object creation:

   - A User must have at least one permission in order to be
     valid.

   - An Account must have at least one user to be valid.
 
   - An Account must have at least one resource to be valid.

  Suppose you want to test an Account. In order to create an Account,
  you must have created an Resource and a User. In order to create a
  User, you must have a Permission.

  If you write the most obvious test code for your Account, your tests
  will have to create a User, a Resource, and a Permission. If you
  later change how your Users and Permissions interact, your Account
  test will break, because even if the interface to User and/or
  Permissions is compatible at the class level, your I{tests} are still
  tightly coupled to the entire object tree. (Obviously, in the real
  world with real models this problem is even more acute.)

  If you try to abstract this out into a function, you will, bit by bit,
  refactor your way into a model where each level of the object graph
  basically has its own function, and you'll eventually refactor your
  way into being able to pass arguments down from a high level to a
  low-level freely.

  Then, you can say something like C{newAccount = data.newAccount()}
  and get a correctly-configured Account object, while still being
  able to change the user's name with something like: C{newAccount =
  Objects.newAccount(use_user: {'name': 'Bob'})}, or so on, even deeper.

  Or you can skip the incremental refinement and just use this module.

How To Use This Module (/Tutorial)
==================================

 Step 1
 ------

  First, find a "leaf object" in your code. This is an object that can
  exist without reference to any other object.

  In the example, this would be a Permission; it is the only object of
  the four that can exist in isolation.

  Create a function that can create this leaf object, using whatever
  relevant parameters you want. For simplicity, Permissions only take
  a 'name'::

       def createPermission(data, name = 'testpermission'):
           return Permission(name)

  The first parameter is the nonmockobjects.Objects object that you
  are using to call this function. 

  Now, register this function with nonmockobjects::

       from nonmockobjects import register
       @register
       def createPermission(name = 'testpermission'):
           return Permission(name)

 Step 2
 ------

  In your test code, create an instance of nonmockobjects.Objects::

       data = nonmockobjects.Objects()

  Now, you can create a permission via the method on data corresponding
  to the name of your function::

       permission = data.createPermission() # is named 'testpermission'

  You can override the name with either normal or keyword args
  (note this will change later)::

       permission = data.createPermission('test2') # is named 'test2'
       permission = data.createPermission(name='test3') # is name 'test3'

  At this point, we've done nothing you couldn't already do, of course.

 Step 3
 ------

  This is where it starts to get interesting.

  Find an object that is the next layer up from your leaf object. In
  this example, it is the User object, which B{must} have a permission,
  which must be passed in as a list of permissions::

       @register
       def createUser(name = 'testuser%(inc)s',
                      email = lambda: 'email sample', 
                      permission = createPermission):
           return User(name, [permission])

  There are some special services nonmockobjects is providing for you,
  as documented in L{register}. Since C{email} is callable, it will
  actually be called each time to generate a default email, if you
  don't pass one in. C{permission = createPermission} indicates that
  we want to create a new permission if one isn't passed in, or that
  we want to use certain arguments to construct a new permission.

  Now you can use data.createUser in several ways:

   - Create a user using a permission you already have in hand (here
     bound to 'permIHave')::

          user = data.createUser(permission = permIHave)

     Passing in an existing permission causes the user to use that.

   - Create a user and simultaneously create a permission with given
     arguments::

          user = data.createUser(usePermission = {'name': 'new permission'})

     This creates a new Permission as if you called
     data.createPermission(name = 'new permission'), then creates a new
     User with that permission.

   - Finally, just create a new user and let the system take care of all
     the necessary Permission creation::

          user = data.createUser()

  Now when you need to test a user, you can create a user with the
  necessary level of detail, and no more. If what you are testing has
  nothing to do with permissions, you can just create one. If you need
  the user to have a certain permission, you can do that too. 

  Note that normal concerns about the mutability of Python keyword
  arguments apply.

 Step 4
 ------

  Repeat Step 3 as needed for all objects you want to test.

  If you continuing creating functions, eventually you'll end up with
  a function "data.createAccount()", which 
  creates multiple objects and ties them together for you, but allows
  you the ability to override any part of that process. For instance, to
  create a permission with a specific name::

       account = data.createAccount(useUser = {'usePermission': {'name':
                                     'specific permission' } } )

  Feel free to add new creation or manipulation methods as needed. For
  instance, if this were an app I would have created an addUserToAccount
  method::

       @register
       def addUserToAccount(account, user = createUser):
           account.addUser(user)

  This allows you to either add a user to an account you already have in
  hand, or allow the nonmockobjects system to simply come up with a new
  user. (Creating functions that can either use existing objects or
  create them on the spot is more useful when you have more parameters
  and more complicated functions; the true power of this approach
  really can't be demonstrated in sample code.)

  In the end, you'll end up with a series of functions that match your
  system's structure, and you can create tests that depend only on what
  you're testing. Thus, if the way Users and Permissions works changes,
  your calls to data.createAccount() need not be changed, except in
  tests directly affected by the changes. No matter how complex your
  object system may get, if you want to test a "leaf" object, all
  you have to do is "objects.leafObject()".

  Using this module makes it practical to test very complicated objects,
  and to write tests that use data as close to production data as
  possible (since this takes the pain out of creating large test
  structures). 

How This Works
==============
  Functions that you @register are used to create methods on the
  nonmockobjects.Objects class. That's why they always take C{data} as
  the first argument; in some sense that's actually C{self}, but that
  would be deceptive I think. (You can use it if you like, of course.)

  As a result, attributes on the Objects object are available to
  functions via the data instance. See the L{Objects} object's
  documentation for the details, but as a quick note, the Objects object
  takes any keyword arguments and sets them as attributes on
  itself. Thus, if your test functions need access to a database
  connection, you can::

      data = nonmockobjects.Objects(db_conn=db_conn)

  and all test creation objects can access the database connection by
  getting the db_conn attribute from their first parameter.

  It is probably a bad idea to use this to communicate amoung creation
  functions, but knock yourself out.

Variations
==========

 Sometimes it is useful to test several variations of a given object;
 this can be useful to test that invariant hold, that a "real account"
 is created for any of several combinations of options, or other
 things.

 NonMockObjects provides a way to quickly generate numerous
 combinations of parameters for creating an object using C{Choose}
 and C{ChooseArgs}.

 Consider the following::

     def permission(data, name = Choose("perm%(inc)s", "SpecialPerm")):
         return Permission(name)

 When you call this as C{data.permission()}, NonMockObjects will
 automatically take the first choice as the "default" for the object,
 resulting in a permission that uses the automatic incrementer to
 create a name.

 However, if you call C{permissions = data.variations_permission()},
 you get an iterator that will yield a series of Permission objects,
 created by making calls to the C{permission} function, using each
 choice once. In this case, it will return two permissions, one using
 the default incrementer, and one being "SpecialPerm", which you may
 want to test for some reason.

 (A different method name is used based on C{variations_*}, because
 returning an object is fundamentally different than returning an
 iterator. Explicit is better than implicit.)

 C{ChooseArgs} is basically the same as Choose, except that instead of
 providing a default value, it provides a series of sub-argument
 specifications. For instance::

     def user(data, name = "User%(inc)s",
              permission = ChooseArgs(permission,
                                      {'name': 'perm1'},
                                      {'name': 'perm2'})):
         return User(name, permission)

 The first argument is the function to use to create the sub-object
 (same as specifying the function without ChooseArgs), and the
 remainder of the arguments are a series of dicts to use as the
 sub-object parameters. In this case, C{data.variations_user()} would
 produce two users, one with the C{perm1} Permission and one with the
 C{perm2} Permission.

 You can have more than one C{Choose} or C{ChooseArgs} in a function
 definition. In that case, NonMockObjects will create one object for
 every combination of choices::

     def user(data, name = Choose("Bob", "Jane", "Spock"),
              permission = ChooseArgs(permission,
                                      {'name': 'perm1'},
                                      {'name': 'perm2'})):
         return User(name, permission)

 This returns six User objects, using each combination of name and
 permissions.

 Because of the danger of the combinations growing rapidly, this
 functionality is not done recursively. If you need that, you should
 explicitly create a new top-level function that dispatches arguments
 as appropriate.
 
 These C{Choose[Args]}-based attributes can be overridden as normal in
 a call::

     users = data.user(name="Me")

 with the previous C{user} function will only return two User objects,
 both named Me but one with C{perm1} and one with C{perm2}.

 Finally, you can add Choose or ChooseArgs on an ad-hoc basis simply
 by passing them in as a parameter. Using the normal::

     def account(data, name = "Account%(inc)s", user = user):
         return Account(name, user)

 you can call::

     accountsToTest = data.variations_account(name=Choose('a', 'b'))

 to an iterator which will produce two accounts, each with a new user,
 one named "a" and one named "b".

 You can also use this to manually limit a choice of many objects to a
 choice of fewer objects, to cut down on the number of choices generated.

Why Do This?
============

 Fundamentally, every difference between your production code and your
 test harness is a place for bugs to live. Every mock object you add
 is a difference between your test harness and your real system, and
 is therefore a place where bugs can live.

 I've been down that road and I didn't like it. It was better than
 nothing, but there were too many things I missed. A half-assed
 combination of mock objects, mostly to satisfy constraints like those
 discussed above, and test-specific hacks to fix a certain test in a
 way not used anywhere else in the system, let alone our production
 code, was getting on my nerves.

 This structure allows you to minimize the number of hacks in your
 testing code by taking the pain out of constructing I{real} objects.

 Mock objects and hacks may still be necessary for performance and
 replicability purposes, but I think they ought to be considered a
 last resort or a performance optimization, not the first thing you
 reach for in a test situation. The exact balance will of course
 depend on your situation.

Hints, Tips, and Tricks
=======================

 You should create a solid naming style for these test functions. I've
 been using "newSomething" for a function that creates something from
 scratch, and "addSomething(target)" for a function that adds a
 something to the given target, where the target must be the first
 argument.

 It is a common pattern to have a function that just sets the default
 parameters for a call to some other function, like so::

      def createSomething(data, a = 1, b = "test%(inc)s", c = 4):
          return Something(a, b, c)

 As the number of parameters grows and the names get long, it is bad
 to have to retype them in the Something call. Consider this instead::

      def createSomething(data, a = 1, b = "test%(inc)s", c = 4):
          return Something(**all_args())

 NonMockObjects provides all_args, which is just like "locals()"
 except it is smart enough to pop off the first argument, which is the
 Objects instance, which you don't need.

 It is possible to put the creation functions for a class in the class
 itself, like::

      class User(object):
          def __init__(self): ...

          @register
          def newUser(data, name):
              return User(name)

 But note that at the time the register decorator is run, it has no way
 (to my knowledge) to know that newUser is in a class specification;
 register recieves a function object, not an unbound method. As a
 result, register can not treat the function specially in any way, so
 it must act just like any other registered function.

 On the one hand, it may be convenient to bundle all test creation
 functions in with the class specification. On the other hand, while
 'newUser' does not really belong to User (it's really a method on
 nonmockobjects.Objects), the User class will still end up with a newUser
 method, which may screw up introspection, may be confusing if
 accidentally called, etc. I don't recommend sticking them in classes.

 The reason I went with functions as the final creation mechanism, and
 not some metadata specification or an attempt to label a
 method/classmethod as the 'creation' technique, or try to introspect
 the class itself, is that you will find that in practice, your real
 functions will end up more complicated than the deliberately-simple
 examples shown here. I use this in a well-normalized-database
 environment (in Django), so I do know it does at least some real-world
 tasks correctly, even relatively complicated ones.

 Write powerful functions, but try to minimize their length; anything
 that can be moved up into the class probably should be. Even so, the
 'core' test code left behind can be surprisingly large. Production
 code I{should not} use any nonmockobjects creation functions; if you are
 tempted to do so, that means you have functionality to move into a
 separate method or function. I find the test code often teaches me
 what convenience methods to add to my code early on, when the test
 code may do something five times but I've only gotten one 'real' use.

 If you have many slightly different functions, do not be afraid to use
 "register_as" in a loop::

      for specialName in [...]:
          def testFunction(arg1, arg2):
              # do things, do something different based on specialName

          register_as('testFunc%s' % specialName)(testFunction)

 Repetitiveness in test code is just as evil as it is anywhere else.

 To take the names of functions and create the "use_function = {}"
 parameter names, nonmockobjects calls
 nonmockobjects.use_prefix(methodName). The 
 default function implements the default Python naming policy, which
 will change 'permission' 
 into 'use_permission', for instance. Feel free to override that
 function (as early as possible) to implement your own local coding
 standards, whatever they may be. The best thing to do may be to
 create a small module that wraps nonmockobjects and overrides that function,
 then use that module instead of nonmockobjects directly.

 This system helps make it easier to start with a truly fresh test
 database, if you've got a database application, as creating test
 accounts of any complexity is just a function call.

 The new Python 2.5 'partial function application' support can be
 really useful with the code you'll produce with this module.
"""

# FIXME: Document variations.
# "In the interests of 'explicit is better than implicit', a separate
# method is used when obtaining variations, because the iterator-based
# interface is fundamantally different than the single-value
# function. The normal function will notice that you passed in a
# Chooser, and give an error message to the effect that you need to
# call the correct method. (This applies when you pass a Chooser in;
# Choosers declared in the initial registration, as mentioned earlier,
# will take their first 'default' choice.)"

from types import StringTypes
from inspect import currentframe, getargvalues

__all__ = ['use_prefix', 'Objects', 'register_as', 'register',
           'call_protect', 'all_args', 'Choose', 'ChooseArgs']

def use_prefix(name):
    """Standard use_prefix function: Implements 'use_' + name.

    @param name: The original name as a string, to be convert to the
    parameter name."""
    return "use_" + name

def variations_prefix(name):
    """Standard variations_prefix function: Implements 'variations_' +
    name.

    @param name: The original name as a string, to be converted to the
    parameter name."""
    return "variations_" + name

def call_protect(callable_object):
    """Protects callables that you really want to pass as a function
    by wrapping it in a function that will return your callable.

    @param callable_object: The callable object to protect."""
    return lambda: callable_object

import itertools
INCREMENTER = itertools.count()

class Objects(object):
    """Objects is the object you instatiate to get access to your
    creation functions.

    Your creation functions actually end up as methods of this class.

    All variables documented here are technically private, but pylint
    and cheese throw a positive fit about all the 'external' entities
    accessing them, even though it's by design...

    @cvar func_to_method: Map the function back to the name of the
    method to use for that attribute.
    @cvar call_name_to_func_name: Maps the use_X back to X. Necessary
    since you can arbitrarily change the use_X transformation.
    @cvar registered: The set of registered functions, so we can check
    that you don't use the same name twice.
    """
    # Map registered functions to their methodname, so we can
    # pick those up in the registration.
    func_to_method = {}
    call_name_to_func_name = {}
    registered = set()
    def __init__(self, **args):
        """This calls self.__dict__.update(args), so you can pass
        anything you want into a Objects construction, and construction
        functions can use that.

        @param args: Things to stick on the Objects object."""
        self.__dict__.update(args)

def register_as(name_override = None):
    """Longer form of register that takes a name_override to set the
    Objects name of the registered function to.

    (This can be necessary when the name you want for the method
    conflicts with another object by the same name; just create a
    function with a throwaway name, and pass in a name_override to
    register_as.).

    @param name_override: The name to use on the Objects object."""
    def decorator(func):
        """This closure-based function implements the decorator.

        @param func: The function we are registering."""
        if name_override is None:
            name = func.func_name
        else:
            name = name_override

        if name in Objects.registered:
            raise ValueError("Can't name method after %s because it "
                             "is already used." % name)
        Objects.registered.add(name)

        # 4 indicates *args use, 8 indicates **kwargs use
        if func.func_code.co_flags & 12:
            raise ValueError("Function being registered for use by "
                             "test data can not use *args or **kwargs.")

        # Get the non-keyword-arguments
        normal_arg_count = func.func_code.co_argcount
        if func.func_defaults:
            normal_arg_count -= len(func.func_defaults)

        # Ignore the first normal arg which is the data instance
        all_args = func.func_code.co_varnames[1:func.func_code.co_argcount]
        normal_args = func.func_code.co_varnames[1:normal_arg_count]
        if func.func_defaults:
            keyword_args = func.func_code.co_varnames[normal_arg_count:
                                                     normal_arg_count +
                                                     len(func.func_defaults)]
            default_args = dict(zip(keyword_args, func.func_defaults))
        else:
            default_args = {}

        # We have the callable. Generate the stub that will be used as
        # a method on the Objects class.
        def method(self, *args, **kwargs):
            "This is a closure that implements the methods on L{Objects}."
            calling_args = dict(zip(all_args, args))

            for att_name, value in default_args.iteritems():
                def process_callable(callable_value):
                    if hasattr(callable_value, 'im_func'):
                        callable_value = callable_value.im_func

                    if callable_value in Objects.func_to_method:
                        method = getattr(self,
                                         Objects.func_to_method[callable_value])
                        calling_args[att_name] = method(**kwargs)
                        if att_name in kwargs:
                            del kwargs[att_name]
                    else:
                        calling_args[att_name] = value()

                # Process the value if it was passed in.
                # Was it passed in as a keyword arg?
                if att_name in kwargs:
                    # (Make sure we know what it is.)
                    if att_name in calling_args:
                        raise TypeError("Too many arguments passed to "
                                        " %s" % name)
                    value = kwargs[att_name]
                    if callable(value):
                        del kwargs[att_name]
                        process_callable(value)
                    else:
                        calling_args[att_name] = kwargs[att_name]

                # Was it passed in as a non-keyword arg?
                if att_name in calling_args:
                    continue

                # If this is a Chooser, extract the default args
                # properly
                if isinstance(value, Chooser):
                    value, choose_default_args = value.default()
                    if choose_default_args and \
                       use_prefix(att_name) not in kwargs:
                        kwargs[use_prefix(att_name)] = choose_default_args

                # Now that we have a default argument in hand,
                # do the special processing this module offers.
                if type(value) in StringTypes and \
                   "%(inc)s" in value:
                    # No default passed in
                    calling_args[att_name] = value % {'inc': INCREMENTER.next()}

                elif callable(value):
                    process_callable(value)
                else:
                    # Use default straight-up
                    calling_args[att_name] = value

            # Verify that all normal args are there, give nicer error
            # message.
            for normal_arg in normal_args:
                if normal_arg not in calling_args:
                    if normal_arg in kwargs:
                        calling_args[normal_arg] = kwargs[normal_arg]
                    else:
                        raise TypeError("Required parameter %s missing "
                                        "from non-keyword arguments."
                                        % normal_arg)

            # Check: No Choosers got through
            for calling_value in calling_args.values():
                if isinstance(calling_value, Chooser):
                    raise ValueError("A Chooser got through to the "
                                     "normal creation function call; " 
                                     "you probably meant to call %s"
                                     % variations_prefix(name))

            return func(self, **calling_args)

        method.func_name = name

        setattr(Objects, method.func_name, method)

        def variations(self, *args, **kwargs):
            """This is a closure that implements the variations method
            for this method."""
            calling_args = dict(zip(all_args, args))
            # Merge that into the kwargs
            kwargs.update(calling_args)

            variables = {}

            for att_name, value in default_args.iteritems():
                use_att_name = use_prefix(att_name)

                # If the use_* parameter was passed directly in,
                # skip over this parameter and pass that through.
                if use_att_name in kwargs:
                    continue

                if att_name in kwargs:
                    value = kwargs[att_name]

                # If this is a normal argument, we don't need to
                # process it.
                if not isinstance(value, Chooser):
                    continue

                # OK, this is a variable.
                variables[att_name] = value

            method = getattr(self, name)
                
            # Now we've collected all the variables. Special case: If
            # there are none, we create an iterator that just returns
            # the 'base case' and then terminates.
            if not variables:
                yield method(**kwargs)
                return

            # Otherwise, we need to permute the variables.
            variables = list(variables.iteritems())

            def permutations(vars):
                if not vars:
                    yield []
                    return

                choices_att_name, choices = vars[0]
                for value, args in choices:
                    for remainder in permutations(vars[1:]):
                        yield [(choices_att_name, value, args)] + remainder

            for choice_permutation in permutations(variables):
                new_kwargs = kwargs.copy()

                # Prepare the arguments for this pass through.
                for att_name, att_value, att_args in choice_permutation:
                    new_kwargs[att_name] = att_value
                    if att_args:
                        use_att_name = use_prefix(att_name)
                        if use_att_name not in kwargs:
                            new_kwargs[use_att_name] = att_args

                object = method(**new_kwargs)
                yield object

        variations.func_name = variations_prefix(name)
        setattr(Objects, variations.func_name, variations)

        # Create this once and stash it in the closure.
        call_name = use_prefix(name)
        Objects.call_name_to_func_name[call_name] = name

        # And generate the stub that will be used internally
        def private_method(self, **kwargs):
            """This is a closure-based function that implements an inner
            function used by the framework.

            @param kwargs: This method is what implements the 'use the
            argument if it's there, use use_* to create it, or use the
            defaults' behavior, so the kwargs are checked for that."""
            if name in kwargs:
                return kwargs[name]

            if call_name in kwargs:
                sub_args = kwargs[call_name]
            else:
                sub_args = {}

            target_method = getattr(self,
                                    self.call_name_to_func_name[call_name]) 

            return target_method(**sub_args)

        private_method.func_name = call_name
        setattr(Objects, call_name, private_method)
        Objects.func_to_method[func] = call_name

        # Return the original function unchanged.
        return func

    return decorator

def register(func = None):
    """Register a function as a non-mock-object creation function.
    Can be used as a decorator.

    register examines the default arguments you provide for the given
    function by using Python introspection, and performs the following
    manipulations when calling your function:

     - If default value is a string containing '%(inc)s', which you'll
       note uses the Python string interpolation syntax, a unique
       number (across all uses of %(inc)s) will be interpolated into
       the string actually passed to the function. This makes it easy
       to create unique ids as needed.

     - If the default value is callable, and you don't provide a value
       in your call, the test system will call that value with no
       arguments and use the resulting value as the value passed into
       the function. Note you can use this with closures or callable
       objects to implement any default behavior you like.

     - As a I{very} special value, as in the example in the module
       documentation, if the callable is actually the
       function reference of a previously-registered creation
       function, we get very special behavior. If the function is
       called without this parameter, the Objects class will be asked to
       create a brand new instance of the object. If the function is
       called with nonmockobjects.use_prefix(func.func_name) (usually
       C{'use_' + func_name}, unless you override), the value is
       expected to be a dict which can be **'ed into arguments for the
       relevant Objects creation method. Finally, if the function is
       called with this parameter, the value will be used without any
       creation; see module documentation for examples.

    If you need to use a callable object as a default argument, and
    you do not want the nonmockobject framework to call it, protect it
    with the C{call_protect} function::

        @register
        def call_func(function: call_protect(lambda x: x + 1)):
            return function(44)

    @param func: The func to register.
"""
    # Nicer error message
    if func is None:
        raise ValueError("nonmockobjects.register should be used as "
                         "@register, not @register()")
        
    return register_as()(func)

class Chooser(object):
    """A superclass for the multiple-choice choosers."""

class Choose(Chooser):
    """Implements a selection of choices for a given parameter."""
    def __init__(self, *choices):
        """Specifies the choices being made available."""
        self.choices = choices

    def default(self):
        """Returns the default choice from the selection, which is the
        first."""
        return self.choices[0], False

    def __iter__(self):
        """Returns the various choices in this Choose."""
        for choice in self.choices:
            yield choice, False

class ChooseArgs(Chooser):
    """Implements a selection of choices to feed to a sub-function."""
    def __init__(self, function, *choices):
        self.function = function
        self.choices = choices

    def default(self):
        """Returns the default choice from the selection, which is the
        first."""
        return self.function, self.choices[0]

    def __iter__(self):
        for choice in self.choices:
            yield self.function, choice

def all_args(*exclude):
    """This gets all the local args of the calling stack frame, but
    filters out the Object instance parameter."""

    try:
        frame = currentframe()
        caller_frame = frame.f_back
        args, _, _, caller_locals = getargvalues(caller_frame)[:4]

        del caller_locals[args[0]]

        for name in exclude:
            if name in caller_locals:
                del caller_locals[name]

    finally:
        del frame
        del caller_frame

    return caller_locals

