"""

    autoself:  automagically add 'self' argument to method definitions.

First, a disclaimer.  Explicit self is good.  Bytecode hacks are bad.
Put them together and it's quite clear that THIS MODULE IS AN ABOMINATION!
But, it's a neat excursion into python's lower levels and if you *really*
*really* want to save yourself some keystrokes (like, you're desperately
trying to hack into the Death Star's security system to override the trash
compactor as its cold metal jaws slowly squeeze you to a purple paste) then
it can help you do that.  But, stop and consider Guido's proclamation on
the matter:

  Having self be explicit is a *good thing*. It makes the code clear by
  removing ambiguity about how a variable resolves. It also makes the
  difference between functions and methods small.
     "Things that will Not Change in Python 3000":
     http://www.python.org/dev/peps/pep-3099/#core-language

This module is not about making 'self' implicit.  It doesn't try to change
the way methods work, or make any semantic changes whatsoever.  It does one
simple thing: automatically adds the 'self' argument to method definitions.
Think of it as a post-processor for method definitions.

It provides a single function <autoself>.  Given a function as argument,
<autoself> will return an equivalent function that takes the variable 'self'
as an extra argument in position zero.  If the function does not refer to a
variable named 'self', then it is returned unmodified.

For example, defining the method <likes>  using:

    def likes(self,ham,eggs):
        print self, "likes", ham, "and", eggs

Is equivalent to defining it in the following way:

    def likes(ham,eggs):
        print self, "likes", ham, "and", eggs
    likes = autoself(likes)

Or neater, using the @autoself decorator.  Of course, this isn't going to save
you any typing!  <autoself> can also be applied to a class, and will autoselfify
all functions in that class's dict:

   class HeapsLessTyping:
      def likes(ham,eggs):
        print self, "likes", ham, "and", eggs
      def hates(spam):
        print self, "hates", spam
   HeapsLessTyping = autoself(HeapsLessTyping)

When its becomes available (Python 2.6?), it will be even more convenient to
use this with the class decorator syntax:

   @autoself
   class HeapsLessTyping:
      def likes(ham,eggs):
        print self, "likes", ham, "and", eggs
      def hates(spam):
        print self, "hates", spam

Want to save even more typing?  <autoself> can be used as a metaclass to
work it's magic on all classes defined in a module:

   __metaclass__=autoself
   class LookNoSelf:
       def __init__(my,special,args):
           self.my = my
           self.special = special
           self.args = args
   class FiveKeystrokesSaved:
       def __init__(this,works,great):
           self.this = this
           self.works = works
           self.great = great

Using this style, you will see a net saving in keystrokes with only
five method definitions per module!

"""

__ver_major__ = 1
__ver_minor__ = 0
__ver_patch__ = 0
__ver_sub__ = ""
__version__ = "%d.%d.%d%s" % (__ver_major__,__ver_minor__,
                              __ver_patch__,__ver_sub__)

import types
import dis
import os
import sys
import unittest

def autoself(obj,cbases=None,cdict=None):
    """Automatic 'self' argument in function definitions.

    This function modifies function definitons to include an automatic 'self'
    argument at position zero.  It can be called with the following types of
    argument:

        * a function:  returns a new function with auto 'self' argument
        * a class:     autoselfifies all applicable methods in class dict
        * other:       returns the object unmodified

    For functions that do not refer to the variable 'self', or already
    have 'self' as their first argument, the function is returned unmodified.

    This function can also be used as a metaclass, if provided with
    the appropriate three arguments instead of the usual one.
    """
    # Three arguments given, assume we're creating a class
    if cbases is not None and cdict is not None:
        klass = type(obj,cbases,cdict)
        return autoself(klass)
    # A proper function - create autoselfified version
    if type(obj) == types.FunctionType:
        fc = obj.func_code
        # Check whether it already has 'self'
        try:
            if fc.co_varnames[0] == 'self':
                return obj
        except IndexError:
            pass
        # Locate 'self' in names and freevars list
        # If it's not in either, the function doesn't refer to self so
        # we do not modify it.
        try:
           selfNM = list(fc.co_names).index('self')
        except ValueError:
            selfNM = -1
        try:
            selfFV = len(fc.co_cellvars) + list(fc.co_freevars).index('self')
        except ValueError:
            selfFV = -1
        if selfNM == -1 and selfFV == -1:
            return obj
        # Add 'self' as the first argument, and fix up the bytecode
        newVars = tuple(['self'] + list(fc.co_varnames))
        newCode = "".join(_fixself(fc.co_code,selfNM,selfFV))
        # Create new code and function objects, and return
        c = types.CodeType(fc.co_argcount+1,fc.co_nlocals+1,fc.co_stacksize+1,
                           fc.co_flags,newCode,fc.co_consts,fc.co_names,newVars,
                           fc.co_filename,fc.co_name,fc.co_firstlineno,
                           fc.co_lnotab,fc.co_freevars,fc.co_cellvars)
        withSelf = types.FunctionType(c,obj.func_globals,obj.func_name,
                                        obj.func_defaults,obj.func_closure)
        return withSelf
    # A class - autoselfify all entries in __dict__
    if type(obj) in (type,types.ClassType):
        for mn in obj.__dict__:
            m = obj.__dict__[mn]
            am = autoself(m)
            # Must use setattr on new-style classes, __dict__ is not writable
            if m is not am:
              setattr(obj,mn,am)
        return obj
    # Something else - do not modify
    return obj

# Opcodes that operate on names/vars, and the corresponding opcode for local
# vars. These need to be translated in the bytecode.
_name2local = { 'STORE_NAME': 'STORE_FAST',
                'DELETE_NAME': 'DELETE_FAST',
                'STORE_GLOBAL': 'STORE_FAST',
                'DELETE_GLOBAL': 'DELETE_FAST',
                'LOAD_NAME': 'LOAD_FAST',
                'LOAD_GLOBAL': 'LOAD_FAST',
                'LOAD_DEREF': 'LOAD_FAST',
                'STORE_DEREF': 'STORE_FAST'}

def _fixself(code,nmIdx,fvIdx):
    """Fix bytecode to treat self as an argument rather than a name.
    <code> is the bytecode to be modified, <nmIdx> and <fvIdx> are the
    position os 'self' in the names and freevars arrays respectively.
    The following transforms are applied:
        * opcodes taking a local as argument have their argument incremented
          by one, to account for the new arg at position zero
        * opcodes treating 'self' as a name are modified to use local var zero
        * opcodes derefrencing cellvar fvIdx are modified to use local var zero
    """
    ops = iter(code)
    for op in ops:
      op = ord(op)
      if op < dis.HAVE_ARGUMENT:
        yield chr(op)
      else:
        arg = ord(ops.next()) + ord(ops.next())*256
        if op in dis.haslocal:
          arg = arg + 1
        elif op in dis.hasname and arg == nmIdx:
          opname = dis.opname[op]
          if opname in _name2local:
            opname = _name2local[opname]
            op = dis.opmap[opname]
            arg = 0
        elif op in dis.hasfree and arg == fvIdx:
          opname = dis.opname[op]
          if opname in _name2local:
            opname = _name2local[opname]
            op = dis.opmap[opname]
            arg = 0
        yield chr(op)
        yield chr(arg % 256)
        yield chr(arg // 256)
            

##  Testsuite begins here

def _test0():
    """A very simple function for testing purposes."""
    return self
class _testC:
    """A very simple class for testing purposes."""
    def __init__(input):
        self.input = input
    def meth1(*args):
        return (self,args)

class TestSimple(unittest.TestCase):
 
    def test_ZeroArg(self):
        """Test whether 'self' is actually inserted"""
        asf = autoself(_test0)
        self.assertEqual(42,asf(42))

    def test_DoubleApp(self):
        """Test whether double application leaves it alone."""
        asf = autoself(_test0)
        asf2 = autoself(asf)
        self.assert_(asf is not _test0)
        self.assert_(asf is asf2)
        
    def test_PosArgs(self):
        """Test whether positional arguments are maintained correctly."""
        def tester(a1,a2):
          if self == self: pass
          return (a1,a2)
        tester = autoself(tester)
        res = tester(None,42,"bacon")
        self.assertEqual(res,(42,"bacon"))

    def test_StarArg(self):
        """Test whethe *arg works correctly."""
        def tester(a1,*arg):
            return (self,a1,arg)
        tester = autoself(tester)
        res = tester("spam",13,"more","args")
        self.assertEqual(res,("spam",13,("more","args")))

    def test_StarKwd(self):
        """Test whether **kwd works correctly."""
        def tester(a1,*arg,**kwd):
            return (self,a1,arg,kwd)
        tester = autoself(tester)
        res = tester("self",13,"pos","args",key1="val1",key2="val2")
        self.assertEqual(res,("self",13,("pos","args"),{"key1":"val1","key2":"val2"}))

    def test_NoSelf(self):
        """Test whether functions without 'self' are left alone."""
        def tester(a1,a2):
            return (a1,a2)
        asf = autoself(tester)
        self.assertEqual(tester,asf)
        self.assertEqual(asf("hi","there"),("hi","there"))


class TestClass(unittest.TestCase):

    def test_BasicClass(self):
        """Test whether classes are transformed correctly."""
        asc = autoself(_testC)
        i = _testC(42)
        self.assertEqual(i.input,42)
        self.assertEqual(i.meth1("ham","eggs"),(i,("ham","eggs")))

    def test_ClassMethod(self):
        """Test whether class methods are left alone."""
        class tester(object):
            def meth1(arg):
                return (self,arg)
            def cmeth(cls,*args):
                return (cls,args)
            cmeth = classmethod(cmeth)
        tester = autoself(tester)
        i = tester()
        self.assertEqual(i.meth1(42),(i,42))
        self.assertEqual(i.cmeth(1,2),(tester,(1,2)))

class TestMetaClass(unittest.TestCase):

    def test_BasicMeta(self):
        """Test whether metaclass definition works."""
        class tester(object):
            __metaclass__ = autoself
            def __init__(color):
              self.color = color
        i = tester("blue")
        self.assertEqual(i.color,"blue")

    def test_ModMeta(self):
        """Test whether module-level metaclass works."""
        import autoself.testmeta


def testsuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSimple))
    suite.addTest(unittest.makeSuite(TestClass))
    suite.addTest(unittest.makeSuite(TestMetaClass))
    return suite

def runtestsuite():
    unittest.TextTestRunner().run(testsuite())

if __name__ == "__main__":
    runtestsuite()

