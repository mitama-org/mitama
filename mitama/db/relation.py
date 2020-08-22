#!/usr/bin/python

from mitama.nodes import db, User, Group
from mitama.db import types

class Relation(db.Model):
    __tablename__ = 'mitama_relation'
    id = Column(types.Integer, primary_key = True)
    parent = Column(types.Group)
    child = Column(types.Node)

