# monkeypatch ZPublisher's call_object so that we can make sure we
# have a trace in each thread before objects are published

# patching approach taken from PDBDebugMode, but I haven't had a
# chance to make this actually coexist with PDBDebugMode yet...

from mr.freeze.freeze import set_thread_trace_when_object_called

from ZPublisher import Publish
from ZPublisher.Publish import missing_name
from ZPublisher.Publish import dont_publish_class
from ZPublisher.Publish import mapply
from Globals import DevelopmentMode

try:
    from Products.PlacelessTranslationService import PatchStringIO
except ImportError:
    from ZPublisher.Publish import publish as real_publish
    USE_PTS = False
else:
    USE_PTS = True
    from ZPublisher.Publish import old_publish as real_publish
    
def pdb_publish(request, module_name, after_list, debug=0,
                call_object=set_thread_trace_when_object_called,
                missing_name=missing_name,
                dont_publish_class=dont_publish_class,
                mapply=mapply, ):
    """Hook the publish function to override the function used to call
    the result of the request traversal."""
    return real_publish(request, module_name, after_list, debug=0,
                call_object=call_object,
                missing_name=missing_name,
                dont_publish_class=dont_publish_class,
                mapply=mapply, )

if DevelopmentMode:

    # call set_thread_trace_when_object_called when the final call for a request is done
    if USE_PTS:
        Publish.zpublisher_publish = Publish.old_publish
        Publish.old_publish = pdb_publish
    else:
        Publish.old_publish = Publish.publish
        Publish.publish = pdb_publish
