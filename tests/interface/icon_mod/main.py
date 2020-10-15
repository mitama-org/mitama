from mitama.app import App, Router, Controller
from mitama.nodes import User
from mitama.app.method import view
from mitama.http import Response
from PIL import Image, ImageDraw
import io

def bold_name(name):
    return '<b>'+name+'</b>'
def italic_screen_name(name):
    return '<i>'+name+'</i>'
def slash_icon(icon):
    img = Image.open(io.BytesIO(icon))
    width, height = img.size
    draw = ImageDraw.Draw(img)
    draw.line(((0,0), (width, height)), fill=(255,0,0), width=10)
    export = io.BytesIO()
    img.save(export, format='PNG')
    return export.getvalue()

User.add_name_proxy(bold_name)
User.add_screen_name_proxy(italic_screen_name)
User.add_icon_proxy(slash_icon)

class HomeController(Controller):
    def handle(self, req):
        user = User.retrieve(int(req.params['id']))
        return Response(text = '<p>'+user.name+'<br>'+user.screen_name+'</p><img src="'+user.icon_to_dataurl()+'" />');

class App(App):
    router = Router([
        view('/<id>', HomeController)
    ])
