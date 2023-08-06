HEADER = '''
  REQUIRES: LINUX OS AND PYTHON3.1

  QUICK TEST: $ python3.1 setup.py build dev --quicktest
'''
FOOTER = '''
RECENT CHANGELOG:
  20091231 - added <<<< and >>>> sugar
  20091224 - added pseudomethod interactive console - revamped pseudomethod import hook
  20091224 - modularized package - fix install issues - added sdist check
  20091209 - improved documentation
  20091205 - moved source code to c++
  20091116 - package integrated

DEMO USAGE:
'''

class numbyte(object):
  description = '''DESCRIPTION: numbyte - numerical bytearray - c++ numerical buffer interface extending bytearrays into numpy-like, 2d arrays'''
  body = '''
  SUMMARY:
  numbyte is a python3.1 c++ extension module.
  numbyte implements a 2d numerical, buffer-like interface for bytearrays, similar to the one described in pep3118.
  numbyte objects can be directly edited by modifying the bytearray they are bound to.
  '''
  footer = '''
  '''
  @staticmethod
  def test():
    ## subclass numbyte
    class numbyte2(numbyte): pass

    ## create bytearray containing 3x4 array of longlong
    integers = numbyte2('i', range(12), shape0 = 3, shape1 = 4)
    print( integers.debug() )

    ## modify underlying bytearray
    integers.bytes()[0] = 0xff; integers.bytes()[1] = 0xff
    print( integers.bytes() )
    print( integers.debug() )

    ## bytearray as sequence
    print( 2 in integers )
    print( integers.count(2) )
    print( integers.index(2) )
    for aa in integers.rows(): print( aa )
    ## slice
    print( integers[1:, 2:].debug() )
    ## transpose
    print( integers.T()[2:, 1:].debug() )
    ## reshape
    print( integers.reshape(2, -1).debug() )
    ## setslice
    integers.T()[2:, 1:] = range(4); print( integers )

    ## almost all arithmetic operations are inplace - use copy to avoid side-effects
    ## recast to double
    floats = integers.recast('f') / 3; print( floats )
    ## copy
    print( floats.copy() + integers[0, :] )
    ## inplace
    print( floats + integers[:, 0] )
    ## inplace
    print( floats - integers[:, 0] )
    ## inplace
    print( floats ** 2 )
    ## inplace
    print( floats.sqrt() )

    ## the only inplace exception are logical comparisons, which return new char arrays
    print( floats )
    ## copy as char
    print( floats == floats[0, :] )
    ## copy as char
    print( floats > 1.5 )
## END















class printstatement(object):
  description = '''DESCRIPTION: printstatement - adds <print<<<< > syntax feature - reintroduce print statements to python3.1'''
  body = '''
  SUMMARY:
  printstatement is a pure python module.
  printstatement is a python ast tree hack, adding the following syntax sugars: <print<<<< >
  '''
  footer = '''
  '''
  @staticmethod
  def test():
    print<<<< 'hello'
    print<<<< 'hello', 'world'
    print<<<< 'hello', 'world' + '!'
    print<<<< 'hello', ('world' + '!'), 'goodbye!'
    aa = 'hello'; print<<<< aa.upper(), 'world'; print<<<< 'hello again'

    ## <print<<<< > FUNCTIONALLY RETURNS <None>
    print( None is print<<<< 1 )

    ## OPERATOR PRECEDENCE
    ## <print<<<< > has similar operator precedence as the comma operator <,>
    # def foo(): return print<<<<  1, 2, 3
    # 1 + print<<<< 1, 2

    # ## <print<<<<> IS A STATEMENT AND HAS NO RETURN TYPE
    # ## the following will raise SyntaxError
    # # def foo(): return print<<<< 1
    # # None == print<<<< 1
## END















class pseudosugar(object):
  description = '''DESCRIPTION: pseudosugar - extend python with functional programming language features'''
  body = '''
  SUMMARY:
  pseudosugar is a pure python module.
  pseudosugar is a python ast tree hack, adding the following syntax sugars:

  function<<<< aa, bb, cc, ... -> function(aa, bb, cc, ...)
  aa, bb, cc, ... >>>>function -> function(aa, bb, cc, ...)

  xx ..function(aa, bb, cc) -> function(xx, aa, bb, cc)
  xx ...function(aa, bb, cc) -> function(aa, xx, bb, cc)
  xx ....function(aa, bb, cc) -> function(aa, bb, xx, cc)
  '''
  footer = '''
  >>> ## start up the interactive console
  >>> from pseudosugar import *
  >>> pseudo_console().interact()

  Python 3.1.1 (r311:74480, Sep 13 2009, 17:17:12)
  [GCC 4.3.2] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (pseudo_console)
  '''.replace('  ', '')
  @staticmethod
  def test():
    #### QUICK EXAMPLES
    ## prefix operator
    print<<<< 'hello', 'world'

    ## postfix operator
    'hello', 'world' >>>>print

    ## pseudomethod
    def function(aa, bb, cc): return (aa, bb, cc)
    1 ..function(0, 0) >>>>print
    2 ...function(0, 0) >>>>print
    3 ....function(0, 0) >>>>print







    ## '<<<<' CONVERTS FUNCTIONS INTO PREFIX OPERATORS
    ## foo<<<< turns foo into a prefix operator
    ## foo<<<< will take in everything to its right that is comma delimited
    ## print<<<< is useful for making print statements
    print<<<< 'bob says', 'hello ' + re.sub<<<< re.compile('(\w+)'), '\\1!', 'world'

    ## '>>>>' CONVERTS FUNCTIONS INTO POSTFIX OPERATORS
    ## it behaves almost exactly like '>>>>' except in reverse
    ## it is useful for chaining together multiple operators
    'qwerty' >>>>list >>>>sorted >>>>enumerate >>>>dict >>>>print

    ## OPERATOR PRECEDENCE
    ## '>>>>' has higher operator precedence than '<<<<'
    print( list<<<< 'abcd' >>>>tuple ) ## list(tuple('abcd'))







    #### PSEUDOMETHOD SYNTAX
    ## DYNAMICALLY BIND FUNCTION CALLS TO OBJECTS
    ## bind the function call print() to 'hello'
    print('hello')
    'hello' ..print()
    'hello' ..print('world')
    'hello' ..print('world', '!')
    'hello' ..print('world', '!', file = sys.stdout)

    ## create a string pseudomethod which adds an exclamation or other endings
    def add_ending(self, end = '!'): return self + end
    'hello' ..add_ending() ..print()
    'hello'.upper() ..add_ending() ..print()
    'hello'.upper() ..add_ending(' world') ..print()
    'hello'.upper() ..add_ending(' world').lower() ..print()
    'hello'.upper() ..add_ending(' world').lower() ..add_ending('!') ..print()
    'hello'.upper() ..add_ending(' world').lower() ..add_ending('!') ..add_ending(end = '!') ..print()



    ## OPERATOR PRECEDENCE
    ## 'aa ..bb()' has the same operator precedence as the attribute operator 'a.b'
    def add(aa, bb): return aa + bb
    print( 2 * 3 ..add(4) + 5 == 2 * (3 + 4) + 5 )
    print( 3 == 1 ..add(2) )
    print( 0, 0 ..add(1), 0 )



    ## EXTEND RESTRICTED TYPES
    ## the python code object type <class 'code'> cannot be subtyped nor will it accept any method binding.
    ## however, we can extend it by dynamically binding ordinary functions.
    ## here's a pseudomethod which disassembles an instance of the type to a specified output
    import dis, io, sys
    def disassemble(self, file):
      backup_stdout = sys.stdout ## backup sys.stdout
      try:
        sys.stdout = file
        dis.dis(self) ## disassemble self
        return file
      finally:
        sys.stdout = backup_stdout ## restore sys.stdout

    code_source = 'print( "hello" )'; code_object = compile(code_source, '', 'exec'); exec( code_object )
    code_object ..disassemble(file = io.StringIO()).getvalue() ..print()



    ## '...' AND '....' SYNTAX
    ## sometimes we instead want the 2nd or 3rd argument of a function bound to an object.
    ## '...' and '....' will do this respectively
    '2nd' ...print(0, 0)
    '3rd' ....print(0, 0)

    ## '....' is useful for chaining re.sub
    ss = 'file = io.StringIO(); print 1, 2, 3 >> file; print file.getvalue()'; print( ss )

    print(
      re.sub('print (.*?)$', 'print( \\1 )',
             re.sub('print (.*) >> (.*?);', 'print( \\1, file = \\2 );', ss)
             )
      )

    ss ....re.sub('print (.*) >> (.*?);', 'print( \\1, file = \\2 );') \
       ....re.sub('print (.*?)$', 'print( \\1 )') \
       ..print()

    ## in fact, another primary use of pseudomethod is to flatten ugly, hard-to-read, lisp-like nested function calls
    print( dict( enumerate( zip( 'abc',  sorted( 'abc bca cab'.split(' '), key = lambda x: x[1] ) ) ) ) )

    'abc bca cab'.split(' ') ..sorted(key = lambda x: x[1]) ...zip('abc') ..enumerate() ..dict() ..print()



    ## IMPORT MODULES WRITTEN WITH PSEUDOMETHOD SYNTAX
    ## create test_module.py
    open('test_module.py', 'w').write('"hello" ..print()\n') ..print('bytes written')

    ## during import, insert the magic prefix 'pseudosugar.' before the last module
    ## import pseudosugar.a
    ## import a.pseudosugar.b
    ## import a.b.pseudosugar.c
    import pseudosugar.test_module
## END















if 'pseudosugar' not in globals(): pseudosugar = numbyte
