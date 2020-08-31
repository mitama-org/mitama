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
    upPropagate = False
    downPropagate = False
    @classmethod
    def accept(cls, node):
        perm = cls()
        perm.node = node
        perm.create()
    @classmethod
    def forbit(cls, node):
        perm = cls.query.filter(cls.node == node).first()
        perm.delete()
    @classmethod
    def is_accepted(cls, node):
        if cls.query.filter(cls.node == node).count() != 0:
            return True
        if node.__class__.__name__ == 'User':
            parents = node.parents()
            for group in parents:
                if cls.is_accepted(group):
                    return True
        if cls.upPropagate:
            for node_ in cls.query.all():
                if node_.node.is_ancester(node):
                    return True
        if cls.downPropagate:
            for node_ in cls.query.all():
                if node_.node.is_descendant(node):
                    return True
        return False
    @classmethod
    def is_forbidden(cls, node):
        return not cls.is_accepted(node)
