#!/usr/bin/python

from mitama.nodes import User, Group, Relation
from mitama.db.types import Column, Integer, Node
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import UniqueConstraint

class PermissionMixin(object):
    '''パーミッションのモデルの実装を支援します

    ホワイトリスト方式の許可システムを実装する上で役に立つ機能をまとめたクラスです。
    このクラスとBaseDatabase.Modelを継承したクラスを定義するとパーミッションシステムを実現できます。

    .. code-block:: python

        class SomePermission(PermissionMixin, db.Model):
            pass

    継承先のクラスで :samp:`target` プロパティを定義した場合、特定のものに対してのみ許可する仕様にすることができます。

    .. code-block:: python

        class SomePermission(PermissionMixin, db.Model):
            target = Column(User)

    targetがUser、またはGroupの場合、targetUpPropagate、 targetDownPropagateを指定すれば、targetに対しても伝播をチェックすることができます。

    :param _id: 固有のID
    :param node: 許可するUser、またはGroupのインスタンス
    :param targetUpPropagate: targetがUser、またはGroupの場合の上向き伝播
    :param targetDownPropagate: targetがUser、またはGroupの場合の下向き伝播
    :param upPropagate: 許可対象のUser、またはGroupの場合の上向き伝播
    :param downPropagate: 許可対象のUser、またはGroupの場合の下向き伝播
    '''
    @declared_attr
    def __tablename__(cls):
        return '__'+cls.__name__.lower()+'_permission'
    @declared_attr
    def __table_args__(cls):
        if hasattr(cls, 'target'):
            unique = UniqueConstraint('node', 'target', name='unique')
        else:
            unique = UniqueConstraint('node', name='unique')
        return (unique, )
    node = Column(Node)
    targetUpPropagate = False
    targetDownPropagate = False
    upPropagate = False
    downPropagate = False
    @classmethod
    def accept(cls, node, target = None):
        '''UserまたはGroupに許可します

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        '''
        perm = cls()
        perm.node = node
        if hasattr(cls, 'target') and target != None:
            perm.target = target
        perm.create()
    @classmethod
    def forbit(cls, node, target = None):
        '''UserまたはGroupの許可を取りやめます

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        '''
        if hasattr(cls, 'target'):
            perm = cls.query.filter(cls.node == node).filter(cls.target == target).first()
        else:
            perm = cls.query.filter(cls.node == node).first()
        if perm!=None:
            perm.delete()
    @classmethod
    def is_accepted(cls, node, target = None):
        '''UserまたはGroupが許可されているか確認します

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        '''
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
            if node_.node == None:
                continue
            if node_.upPropagate and not isinstance(node_.node, User) and node_.node.is_ancestor(node) and node_.is_target(target):
                return True
            if node_.downPropagate and not isinstance(node_.node, User) and node_.node.is_descendant(node) and node_.is_target(target):
                return True
        return False
    def is_target(self, target = None):
        if not hasattr(self, 'target'):
            return True
        if self.target == None:
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
        '''UserまたはGroupが許可されていないか確認します

        :param node: UserまたはGroupのインスタンス
        :param target: 許可対象
        '''
        if not hasattr(cls, 'target'):
            return not cls.is_accepted(node)
        else:
            return not cls.is_accepted(node, target)
