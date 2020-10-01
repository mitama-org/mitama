from mitama.server import run_app
from mitama.server.response import Response

def app(request):
    if request.method == 'POST':
        post = request.post()
        print(post['some'])
    return Response(text='''
<!DOCTYPE html>
<html>
    <body>
        <form method='POST'>
            <input type='text' name='some'>
            <button>submit</button>
        </form>
    </body>
</html>
                    ''')

run_app(app, 8080)
