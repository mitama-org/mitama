from . import Metadata, urls
from mitama.app import App

meta = Metadata()
app = App(meta)


app.router.add_routes(urls.urls)
