from mitama.db.driver.sqlite3 import get_test_engine 
from mitama.db import _CoreDatabase
from mitama.db import types

engine = get_test_engine()
db = _CoreDatabase(engine)
from mitama.nodes import User, Group, Relation
from mitama.permission import PermissionMixin

class HogePermission(PermissionMixin, db.Model):
    upPropagate = True
    pass

class PiyoPermission(PermissionMixin, db.Model):
    pass

class FugaPermission(PermissionMixin, db.Model):
    downPropagate = True
    pass

class HogeTargetedPermission(PermissionMixin, db.Model):
    target = types.Column(types.Group)
    targetUpPropagate = True
    pass

class PiyoTargetedPermission(PermissionMixin, db.Model):
    target = types.Column(types.Group)
    pass

class FugaTargetedPermission(PermissionMixin, db.Model):
    target = types.Column(types.Group)
    targetDownPropagate = True
    pass

class HogePiyoTargetedPermission(PermissionMixin, db.Model):
    target = types.Column(types.Group, nullable = True)
    pass

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

def test_up_propagate():
    HogePermission.accept(g[2])
    assert HogePermission.is_accepted(g[0])
    assert HogePermission.is_accepted(g[1])
    assert HogePermission.is_accepted(g[2])
    assert HogePermission.is_accepted(u[0])
    assert HogePermission.is_accepted(u[1])
    assert HogePermission.is_accepted(u[2])
    assert HogePermission.is_forbidden(g[3])
    assert HogePermission.is_forbidden(g[4])
    assert HogePermission.is_forbidden(u[3])
    assert HogePermission.is_forbidden(u[4])

def test_no_propagate():
    PiyoPermission.accept(g[2])
    assert PiyoPermission.is_accepted(g[2])
    assert PiyoPermission.is_accepted(u[2])
    assert PiyoPermission.is_forbidden(g[0])
    assert PiyoPermission.is_forbidden(g[1])
    assert PiyoPermission.is_forbidden(u[0])
    assert PiyoPermission.is_forbidden(u[1])
    assert PiyoPermission.is_forbidden(g[3])
    assert PiyoPermission.is_forbidden(g[4])
    assert PiyoPermission.is_forbidden(u[3])
    assert PiyoPermission.is_forbidden(u[4])

def test_down_propagate():
    FugaPermission.accept(g[2])
    assert FugaPermission.is_accepted(g[3])
    assert FugaPermission.is_accepted(g[4])
    assert FugaPermission.is_accepted(g[2])
    assert FugaPermission.is_accepted(u[3])
    assert FugaPermission.is_accepted(u[4])
    assert FugaPermission.is_accepted(u[2])
    assert FugaPermission.is_forbidden(g[0])
    assert FugaPermission.is_forbidden(g[1])
    assert FugaPermission.is_forbidden(u[0])
    assert FugaPermission.is_forbidden(u[1])

def test_target_up_propagate():
    HogeTargetedPermission.accept(u[2], g[2])
    assert HogeTargetedPermission.is_accepted(u[2], g[0])
    assert HogeTargetedPermission.is_accepted(u[2], g[1])
    assert HogeTargetedPermission.is_accepted(u[2], u[0])
    assert HogeTargetedPermission.is_accepted(u[2], u[1])
    assert HogeTargetedPermission.is_accepted(u[2], g[2])
    assert HogeTargetedPermission.is_forbidden(u[2], u[3])
    assert HogeTargetedPermission.is_forbidden(u[2], u[4])
    assert HogeTargetedPermission.is_forbidden(u[2], g[3])
    assert HogeTargetedPermission.is_forbidden(u[2], g[4])

def test_target_propagate():
    PiyoTargetedPermission.accept(u[2], g[2])
    assert PiyoTargetedPermission.is_forbidden(u[2], g[0])
    assert PiyoTargetedPermission.is_forbidden(u[2], g[1])
    assert PiyoTargetedPermission.is_forbidden(u[2], u[0])
    assert PiyoTargetedPermission.is_forbidden(u[2], u[1])
    assert PiyoTargetedPermission.is_accepted(u[2], g[2])
    assert PiyoTargetedPermission.is_forbidden(u[2], u[3])
    assert PiyoTargetedPermission.is_forbidden(u[2], u[4])
    assert PiyoTargetedPermission.is_forbidden(u[2], g[3])
    assert PiyoTargetedPermission.is_forbidden(u[2], g[4])

def test_target_down_propagate():
    FugaTargetedPermission.accept(u[2], g[2])
    assert FugaTargetedPermission.is_forbidden(u[2], g[0])
    assert FugaTargetedPermission.is_forbidden(u[2], g[1])
    assert FugaTargetedPermission.is_forbidden(u[2], u[0])
    assert FugaTargetedPermission.is_forbidden(u[2], u[1])
    assert FugaTargetedPermission.is_accepted(u[2], g[2])
    assert FugaTargetedPermission.is_accepted(u[2], u[3])
    assert FugaTargetedPermission.is_accepted(u[2], u[4])
    assert FugaTargetedPermission.is_accepted(u[2], g[3])
    assert FugaTargetedPermission.is_accepted(u[2], g[4])

def test_target_none_propagate():
    HogePiyoTargetedPermission.accept(u[3])
    assert HogePiyoTargetedPermission.is_accepted(u[3], g[0])
    assert HogePiyoTargetedPermission.is_accepted(u[3], u[0])
    assert HogePiyoTargetedPermission.is_accepted(u[3], u[1])
    assert HogePiyoTargetedPermission.is_accepted(u[3], g[2])
    assert HogePiyoTargetedPermission.is_accepted(u[3], u[2])
    assert HogePiyoTargetedPermission.is_accepted(u[3], u[4])
    assert HogePiyoTargetedPermission.is_accepted(u[3], g[3])
    assert HogePiyoTargetedPermission.is_accepted(u[3], g[4])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], g[0])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], g[1])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], u[0])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], u[1])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], g[2])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], u[2])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], u[4])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], g[3])
    assert HogePiyoTargetedPermission.is_forbidden(u[4], g[4])


