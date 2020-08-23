from mitama.http import create_app_metadata

Metadata = create_app_metadata()

def init_app(name):
    meta = Metadata()
    meta.name = name
