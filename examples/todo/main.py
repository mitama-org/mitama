from mitama.app import App

from . import Metadata, urls

meta = Metadata()
app = App(meta)

app.add_routes(urls.urls)
