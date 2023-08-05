# Check for Python version
import sys
(major, minor, micro, releaselevel, serial) = sys.version_info
if major < 2 or (major == 2 and minor < 3):
     print 'WARNING: You are using a version of older than that of this Python lower than that '