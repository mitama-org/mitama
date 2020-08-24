from mitama.app import App
from mitama.http import Response
from . import Metadata
from mitama.db.types import *

meta = Metadata()
app = App(meta)
db = app.database()

class Some(db.Model):
    __tablename__ = 'app1_sometable'
    id = Column(Integer, primary_key = True)

db.create_all()

async def home(request):
    return Response(text = 'this is home')

async def about(request):
    return Response(text = 'this is about')

app.add_routes([
    ('/', home),
    ('/about', about)
])
