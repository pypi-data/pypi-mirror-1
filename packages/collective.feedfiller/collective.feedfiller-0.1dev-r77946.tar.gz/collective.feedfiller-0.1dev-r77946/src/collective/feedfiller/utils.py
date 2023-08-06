
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

def get_storage( context, key ):
    annotations = IAnnotations( context )
    if not annotations.has_key( key ):
        annotations[ key ] = PersistentDict()
    return annotations[key]
