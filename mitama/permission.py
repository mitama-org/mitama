#!/usr/bin/python

from mitama.nodes import User, Group, Relation
from mitama.db.types import Column, Integer, Node
from sqlalchemy.ext.declarative import declared_attr

class PermissionMixin(object):
    @declared_attr
    def __tablename__(cls):
        return '__'+cls.__name__.lower()+'_permission'
    id = Column(Integer, primary_key = True)
    node = Column(Node)
    targetUpPropagate = False
    targetDownPropagate = False
    upPropagate = False
    downPropagate = False
    @classmethod
    def accept(cls, node, target = None):
        perm = cls()
        perm.node = node
        if hasattr(cls, 'target') and target != None:
            perm.target = target
        perm.create()
    @classmethod
    def forbit(cls, node, target = None):
        if hasattr(cls, 'target'):
            perm = cls.query.filter(cls.node == node).first()
        else:
            perm = cls.query.filter(cls.node == node).filter(cls.target == target).first()
        perm.delete()
    @classmethod
    def is_accepted(cls, node, target = None):
        perms = cls.query.filter(cls.node == node).all()
        for perm in perms:
            if perm.is_target(target) or perm.is_target(None):
                return True
        if node.__class__.__name__ == 'User':
            parents = node.parents()
            for group in parents:
                if cls.is_accepted(group, target):
                    return True
        for node_ in cls.query.all():
            if cls.upPropagate and node_.node.is_ancestor(node) and node_.is_target(target):
                return True
            if cls.downPropagate and node_.node.is_descendant(node) and node_.is_target(target):
                return True
        return False
    def is_target(self, target = None):
        if not hasattr(self, 'target'):
            return True
        if self.target == target:
            return True
        if isinstance(target, User) or isinstance(target, Group):
            if self.targetUpPropagate:
                return self.target.is_ancestor(target)
            elif self.targetDownPropagate:
                return self.target.is_descendant(target)
            else:
                return self.target == target
        elif self.target == target:
            return True
        return False
    @classmethod
    def is_forbidden(cls, node, target = None):
        if not hasattr(cls, 'target'):
            return not cls.is_accepted(node)
        else:
            return not cls.is_accepted(node, target)
