from mitama.db import BaseDatabase, func, ForeignKey, relationship, Table, backref
from mitama.db.types import Column, Integer, LargeBinary
from mitama.db.types import Node as NodeType
from mitama.db.types import String
from mitama.db.model import UUID

from .core_db import db
from .nodes import User, Group, UserGroup

role_user = Table(
    "mitama_role_user",
    db.metadata,
    Column("role_id", String(64), ForeignKey("mitama_role._id", ondelete="CASCADE")),
    Column("user_id", String(64), ForeignKey("mitama_user._id", ondelete="CASCADE"))
)

role_group = Table(
    "mitama_role_group",
    db.metadata,
    Column("role_id", String(64), ForeignKey("mitama_role._id", ondelete="CASCADE")),
    Column("group_id", String(64), ForeignKey("mitama_group._id", ondelete="CASCADE"))
)


class Role(db.Model):
    __tablename__ = "mitama_role"
    screen_name = Column(String(64), unique=True, nullable=False)
    name = Column(String(64))
    users = relationship(
        "User",
        secondary=role_user,
        backref="roles",
        cascade="all, delete"
    )
    groups = relationship(
        "Group",
        secondary=role_group,
        backref="roles",
        cascade="all, delete"
    )

    def append(self, node):
        if isinstance(node, Group):
            self.groups.append(node)
        else:
            self.users.append(node)
        self.update()

    def remove(self, node):
        if isinstance(node, Group):
            self.groups.remove(node)
        else:
            self.users.remove(node)
        self.update()


role_relation = Table(
    "mitama_role_relation",
    db.metadata,
    Column("_id", String(64), default=UUID(), primary_key=True),
    Column("role_id", String(64), ForeignKey("mitama_inner_role._id", ondelete="CASCADE")),
    Column("relation_id", String(64), ForeignKey("mitama_user_group._id", ondelete="CASCADE"))
)

class RoleRelation(db.Model):
    __table__ = role_relation
    _id = role_relation.c._id
    role_id = role_relation.c.role_id
    relation_id = role_relation.c.relation_id

class InnerRole(db.Model):
    __tablename__ = "mitama_inner_role"
    screen_name = Column(String(64), unique=True, nullable=False)
    name = Column(String(64))
    relations = relationship(
        "UserGroup",
        secondary=role_relation,
        backref="roles",
        cascade="all, delete"
    )

    def append(self, group, user):
        relation = UserGroup.retrieve(group=group, user=user)
        self.relations.append(relation)
        self.update()

    def remove(self, group, user):
        relation = UserGroup.retrieve(group=group, user=user)
        self.relations.remove(relation)
        self.update()

    def exists(self, group, user):
        relation = UserGroup.retrieve(group=group, user=user)
        return relation in self.relations


