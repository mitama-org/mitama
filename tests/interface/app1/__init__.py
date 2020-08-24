from mitama.app import BaseMetadata

class Metadata(BaseMetadata):
    pass

def init_app(name):
    meta = Metadata()
    meta.name = name
