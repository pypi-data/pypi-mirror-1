from __future__ import pseudomethod
from itertools import *

"""
USAGE:
@ command line type: python3.0 -c "import pseudomethod; import pseudomethod_test"

the output should look like:

testing pseudomethod example 0
testing pseudomethod example 1
testing pseudomethod example 2
testing pseudomethod example 3
"""

if 1:
  print( "testing pseudomethod example 0" )
  x = set(enumerate(["a", "b", "c"]))
  y = ["a", "b", "c"] .__pseudomethod__.enumerate() .__pseudomethod__.set()
  z = ["a", "b", "c"]                 ..enumerate()                 ..set()
  assert x == y == z == { (0, "a"), (1, "b"), (2, "c") }

  print( "testing pseudomethod example 1" )
  x = min(len("hello world"), 0, 1 + 2)
  y = "hello world" ..len() ..min(0, 1 + 2)
  assert x == y == 0

  print( "testing pseudomethod example 2" )
  def foo(a, b = 0): return a + b
  def bar(c, d = 1): return c * d
  x = bar(foo(1, b = 2), **{"d":3})
  y = 1 ..foo(b = 2) ..bar(**{"d":3})
  assert x == y == 9

  print( "testing pseudomethod example 3" )
  x = eval(compile("oct(16)", "", "eval", 0), globals(), {})
  y = "oct(16)" ..compile("", "eval", 0) ..eval(globals(), {})
  assert x == y == "0o20"

## regression test
if 1:
  print( "testing pseudomethod regressions" )
  assert "a..b" != "a.__pseudomethod__.b"
  assert b"a..b" != b"a.__pseudomethod__.b"
  assert bytearray(b"a..b") != bytearray(b"a.__pseudomethod__.b")
