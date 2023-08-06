from constructs import StoredEntity
from stores import FileStorageFactory

URI_BASE = "info:local/"
STORAGE_DIR = "./rdffilestore"
SPECIAL_FILE_PREFIX = "."

class FileEntityFactory(object):
    def __init__(self, uri_base=URI_BASE, storage_dir=STORAGE_DIR, prefix=SPECIAL_FILE_PREFIX, shorty_length=2):
        """uri_base must end in an /, : or an #. If neither is present a / will be appended."""
        if not(uri_base.endswith('/') or uri_base.endswith('#') or uri_base.endswith(':')):
            uri_base = "%s/" % uri_base
        factory_f = FileStorageFactory()
        self.s = factory_f.get_store(uri_base, storage_dir, prefix, shorty_length)
        # The store might have a different idea on what the prefix is:
        self.uri_base = self.s.uri_base
        

    def get_id(self, id=None):
        uri = "%s%s" % (self.uri_base, id)
        s = StoredEntity(uri)
        s.init(id, self.s)
        return s

    def get(self, uri):
        if uri.startswith(self.uri_base):
            id = uri[len(self.uri_base):]
        s = StoredEntity(uri)
        s.init(id, self.s)
        return s
        
