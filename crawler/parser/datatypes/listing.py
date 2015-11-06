import json

# We might want to move this elsewhere later

# Define the common schema for a listing
# This should be a serializable object, like dict, so we can easily dump the data to json
class Listing(dict):
    # Defined keys are the only ones allowed, in order to enforce the schema
    _keys = ['price', 'mlsnumber']
    
    def __init__(self, *args, **kw):
        super(Listing, self).__init__(*args, **kw)
        #self.itemlist = super(Listing, self).keys()
    
    def __setitem__(self, key, value):
        # Throw an exception if the key isn't in the pre-defined list of valid keys
        
        super(Listing, self).__setitem__(key, value)
        
    def valid(self):
        # TODO: verify the data as much as possible
        if 'price' in self and self['price'] > 0:
            return 1
        return 0
        
    def to_json(self):
        return json.dumps(self)