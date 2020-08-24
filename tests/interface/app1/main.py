from . import Metadata, urls
from mitama.app import App

meta = Metadata()
app = App(meta)

app.add_routes(urls.urls)
