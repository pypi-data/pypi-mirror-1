class ObjectNotFoundException(Exception):
    """Object not found at the ID specified"""
    pass

class ObjectAlreadyExistsException(Exception):
    """Object ID already exists"""
    pass
    
class FedoraStoreFailure(Exception):
    """Fedora failed to store or read an item correctly."""
    def __init__(self, resp, content, action):
        self.resp = resp
        self.content = content
        self.action = action
    
    def __repr__(self):
        return "Fedora failed with a status code of %s upon performing action:'%s'\n\nHeaders: %s\nContent: %s" % (self.resp.status, self.action, self.resp, self.content)
