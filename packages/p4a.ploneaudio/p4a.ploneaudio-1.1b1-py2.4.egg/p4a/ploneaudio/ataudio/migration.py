import os
import tempfile
from zope import interface
from zope import component
from zope import event
from zope.app.event import objectevent
from p4a.audio.migration import IMigratable
from p4a.fileimage import utils as fileutils
from Products.ExternalStorage import filewrapper

class ATAudioMigratable(object):
    interface.implements(IMigratable)
    
    def __init__(self, container, context):
        self.container = container
        self.context = context
        
    def migrate(self):
        orig_id = self.context.getId()
        orig_obj = self.context.aq_base
        
        field = orig_obj.getPrimaryField()
        file = field.getEditAccessor(orig_obj)()
        if isinstance(file, filewrapper.FileWrapper):
            fd, tempfilename = tempfile.mkstemp('.mp3', 'ATAudioMigratable__temp__')
            f = open(tempfilename, 'wb')
            for x in file.filestream():
                f.write(x)
            f.close()
        else:
            tempfilename = fileutils.write_to_tempfile(file)
        
        self.container.manage_delObjects([orig_id])

        self.container.invokeFactory('File', orig_id)
        file = self.container[orig_id]
        f = open(tempfilename, 'rb')
        file.setFile(f)
        f.close()
        
        os.remove(tempfilename)
        
        evt = objectevent.ObjectModifiedEvent(file)
        event.notify(evt)

        return True
