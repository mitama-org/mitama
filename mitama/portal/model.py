from mitama.db.types import *
from mitama.nodes import User, Group
from mitama.db import BaseDatabase
from base64 import b64encode
import magic
from mitama.permission import PermissionMixin

class Database(BaseDatabase):
    pass

db = Database()

class Invite(db.Model):
    icon = Column(LargeBinary)
    screen_name = Column(String)
    name = Column(String)
    token = Column(String, unique = True)
    editable = Column(Boolean)
    def icon_to_dataurl(self):
        f = magic.Magic(mime = True, uncompress = True)
        mime = f.from_buffer(self.icon)
        return 'data:'+mime+';base64,'+b64encode(self.icon).decode()

class CreateUserPermission(PermissionMixin, db.Model):
    upPropagate = True
    pass

class UpdateUserPermission(PermissionMixin, db.Model):
    upPropagate = True
    targetDownPropagate = True
    target = Column(User.type, nullable = True)
    pass

class DeleteUserPermission(PermissionMixin, db.Model):
    upPropagate = True
    pass

class CreateGroupPermission(PermissionMixin, db.Model):
    upPropagate = True
    pass

class UpdateGroupPermission(PermissionMixin, db.Model):
    upPropagate = True
    targetDownPropagate = True
    target = Column(Group.type, nullable = True)
    pass

class DeleteGroupPermission(PermissionMixin, db.Model):
    upPropagate = True
    pass

class Admin(PermissionMixin, db.Model):
    upPropagate = True
    pass

db.create_all()
