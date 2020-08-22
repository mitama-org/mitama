from mitama.conf import Config
import os

def test_config():
    testconf = {
        'apps': [
            {
                'include': 'app1',
                'path': '/'
            },
            {
                'include': 'app2',
                'path': '/app2'
            }
        ]
    }
    conf = Config(os.getcwd(), testconf)
    assert testconf == conf.to_dict()
