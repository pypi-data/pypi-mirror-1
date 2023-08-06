"""
Get the best JSON encoder/decoder available on this system.
"""

__version__ = "0.1"
__author__ = "Rune Halvorsen <runefh@gmail.com>"
__homepage__ = "http://bitbucket.org/runeh/anyjson/"
__docformat__ = "restructuredtext"

"""

.. function:: serialize(obj)

    Serialize the object to JSON.

.. function:: deserialize(obj)

    Deserialize JSON-encoded object to a Python object.

"""

# Try to import a module that provides json parsing and emitting, starting
# with the fastest alternative and falling back to the slower ones.
try:
    # cjson is the fastest
    import cjson
    serialize = cjson.encode
    deserialize = cjson.decode
except ImportError:
    try:
        # Then try to find simplejson. Later versions has C speedups which
        # makes it pretty fast.
        import simplejson
        serialize = simplejson.dumps
        deserialize = simplejson.loads
    except ImportError:
        try:
            # Then try to find the python 2.6 stdlib json module.
            import json
            serialize = json.dumps
            deserialize = json.loads
        except ImportError:
            try:
                # If all of the above fails, try to fallback to the simplejson
                # embedded in Django.
                from django.utils import simplejson
                serialize = simplejson.dumps
                deserialize = simplejson.loads
            except:
                raise ImportError("No json module found")

