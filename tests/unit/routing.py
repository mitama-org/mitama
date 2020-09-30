from mitama.app.router import Router, Route, Path
from mitama.app.method import *

def test_router():
    path_a=Path('/huga/<name>')
    path_e=Path('/huga/<id:int>')
    path_f=Path('/huga/<id:float>')
    path_a_=Path('/huga/<name>/hoge')
    path_b=Path('/hogera/<path:re:.*>')
    path_b_=Path('/hogera/<path:path>')
    assert path_a.match('/huga/boke0')
    assert path_e.match('/huga/0')
    assert path_f.match('/huga/0.1')
    assert not path_a.match('/huga/boke0/hoge')
    assert path_a_.match('/huga/boke0/hoge')
    assert path_b.match('/hogera/var/www/html') == {
        'path': 'var/www/html'
    }
    assert path_b_.match('/hogera/hogera.py') == {
        'path': 'hogera.py'
    }


