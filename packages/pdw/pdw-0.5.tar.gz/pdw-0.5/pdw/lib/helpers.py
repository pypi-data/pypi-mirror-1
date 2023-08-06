"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *
from routes import url_for
try:
    from webhelpers.rails import *
except:
    pass
