_info = """
pascut Automation Flash build tool
version %s
"""
VERSION = (0, 1, 1)
if VERSION[2] is not None:
    version = "%d.%d.%s" % VERSION
else:
    version = "%d.%d" % VERSION[:2]

version_info = _info % version



