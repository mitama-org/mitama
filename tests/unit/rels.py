from mitama.db.driver.sqlite3 import get_test_engine 
from mitama.db import _CoreDatabase

engine = get_test_engine()
db = _CoreDatabase(engine)
from mitama.nodes import User, Group, Relation
db.create_all()

u = list()
for i in range(5):
    u_ = User()
    u_.name = 'test'+str(i)
    u_.screen_name = 'test'+str(i)
    u_.password = ''
    u_.create()
    u.append(u_)

g = list()
for i in range(5):
    g_ = Group()
    g_.name = 'test'+str(i)
    g_.screen_name = 'test'+str(i)
    g_.create()
    g_.append(u[i])
    g.append(g_)
    if i > 0:
        g[i-1].append(g[i])

def test_ancestor():
    assert g[4].is_ancestor(g[0])
    assert g[4].is_ancestor(g[1])
    assert g[4].is_ancestor(g[2])
    assert g[4].is_ancestor(g[3])
    assert not g[4].is_ancestor(g[4])
    assert not g[0].is_ancestor(g[4])
    assert not g[1].is_ancestor(g[4])
    assert not g[2].is_ancestor(g[4])
    assert not g[3].is_ancestor(g[4])

def test_descendant():
    assert g[0].is_descendant(g[4])
    assert g[1].is_descendant(g[4])
    assert g[2].is_descendant(g[4])
    assert g[3].is_descendant(g[4])
    assert not g[4].is_descendant(g[4])
    assert not g[4].is_descendant(g[0])
    assert not g[4].is_descendant(g[1])
    assert not g[4].is_descendant(g[2])
    assert not g[4].is_descendant(g[3])
