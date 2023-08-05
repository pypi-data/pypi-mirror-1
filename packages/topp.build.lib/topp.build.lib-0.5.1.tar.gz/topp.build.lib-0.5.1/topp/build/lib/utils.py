"""
generic functions specific to topp's build library
"""

namespace='topp.build' # master namespace for TOPP's buildy stuff
def appname(app):
    "return full python namespace of app"
    return '.'.join((namespace, app))
