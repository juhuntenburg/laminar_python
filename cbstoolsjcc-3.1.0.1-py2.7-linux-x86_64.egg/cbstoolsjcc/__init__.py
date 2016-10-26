
import os, _cbstoolsjcc

__dir__ = os.path.abspath(os.path.dirname(__file__))

class JavaError(Exception):
  def getJavaException(self):
    return self.args[0]
  def __str__(self):
    writer = StringWriter()
    self.getJavaException().printStackTrace(PrintWriter(writer))
    return "\n".join((super(JavaError, self).__str__(), "    Java stacktrace:", str(writer)))

class InvalidArgsError(Exception):
  pass

_cbstoolsjcc._set_exception_types(JavaError, InvalidArgsError)

VERSION = "3.1.0.1"
CLASSPATH = [os.path.join(__dir__, "cbstools.jar"), os.path.join(__dir__, "cbstools-lib.jar"), os.path.join(__dir__, "commons-math3-3.5.jar"), os.path.join(__dir__, "Jama-mipav.jar")]
CLASSPATH = os.pathsep.join(CLASSPATH)
_cbstoolsjcc.CLASSPATH = CLASSPATH
_cbstoolsjcc._set_function_self(_cbstoolsjcc.initVM, _cbstoolsjcc)

from _cbstoolsjcc import *
