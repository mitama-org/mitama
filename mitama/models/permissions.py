from mitama.db import DatabaseManager, ForeignKey, relationship, Table
from mitama.db.types import Column
from mitama.db.types import String
from sqlalchemy import event


def permission(db_, permissions):
    from .nodes import User, Group, UserGroup, Role, InnerRole
    role_permission = Table(
        db_.Model.prefix + "_role_permission",
        db_.metadata,
        Column(
            "role_id",
            String(64),
            ForeignKey("mitama_role._id", ondelete="CASCADE"),
            primary_key=True
        ),
        Column(
            "permission_id",
            String(64),
            ForeignKey(
                db_.Model.prefix + "_permission._id",
                ondelete="CASCADE"
            ),
            primary_key=True
        ),
        extend_existing=True
    )

    class Permission(db_.Model):
        name = Column(String(64))
        screen_name = Column(String(64), unique=True)
        roles = relationship(
            "Role",
            secondary=role_permission,
            cascade="all, delete"
        )

        @classmethod
        def accept(cls, screen_name, role):
            """特定のRoleに許可します """
            permission = cls.retrieve(screen_name=screen_name)
            permission.roles.append(role)
            permission.update()

        @classmethod
        def forbit(cls, screen_name, role):
            """UserまたはGroupの許可を取りやめます """
            permission = cls.retrieve(screen_name=screen_name)
            permission.roles.remove(role)
            permission.update()

        @classmethod
        def is_accepted(cls, screen_name, node):
            """UserまたはGroupが許可されているか確認します
            """
            perm = cls.retrieve(screen_name=screen_name)
            for role in perm.roles:
                if isinstance(node, User):
                    if node in role.users:
                        return True
                    for group in role.groups:
                        if group.is_in(node):
                            return True
                else:
                    if node in role.groups:
                        return True
            return False

        @classmethod
        def is_forbidden(cls, screen_name, node):
            """UserまたはGroupが許可されていないか確認します
            """
            return not cls.is_accepted(screen_name, node)

    def after_create(target, conn, **kw):
        try:
            DatabaseManager.start_session()
            for perm_ in permissions:
                perm = Permission()
                perm.name = perm_["name"]
                perm.screen_name = perm_["screen_name"]
                db_.session.add(perm)
            db_.session.commit()
        except Exception as err:
            print(err)
            DatabaseManager.rollback_session()
        finally:
            DatabaseManager.close_session()

    event.listen(Permission.__table__, "after_create", after_create)

    return Permission


def inner_permission(db_, permissions):
    from .nodes import User, Group, Node, UserGroup, Role, InnerRole

    inner_role_permission = Table(
        db_.Model.prefix + "_inner_role_permission",
        db_.metadata,
        Column(
            "role_id",
            String(64),
            ForeignKey("mitama_inner_role._id", ondelete="CASCADE")
        ),
        Column(
            "permission_id",
            String(64),
            ForeignKey(
                db_.Model.prefix + "_inner_permission._id",
                ondelete="CASCADE"
            )
        ),
        extend_existing=True
    )

    class InnerPermission(db_.Model):
        name = Column(String(64))
        screen_name = Column(String(64), unique=True)
        roles = relationship(
            "InnerRole",
            secondary=inner_role_permission,
            cascade="all, delete"
        )

        @classmethod
        def accept(cls, screen_name, role):
            """特定のRoleに許可します """
            permission = cls.retrieve(screen_name=screen_name)
            permission.roles.append(role)
            permission.update()

        @classmethod
        def forbit(cls, screen_name, role):
            """UserまたはGroupの許可を取りやめます """
            permission = cls.retrieve(screen_name=screen_name)
            permission.roles.remove(role)
            permission.update()

        @classmethod
        def is_accepted(cls, screen_name, group, user):
            """UserまたはGroupが許可されているか確認します
            """
            if isinstance(group, Node):
                group = group.object
                if isinstance(group, User):
                    return False
            rel = UserGroup.retrieve(user=user, group=group)
            permission = cls.retrieve(screen_name=screen_name)
            for role in permission.roles:
                if rel in role.relations:
                    return True
            return False

        @classmethod
        def is_forbidden(cls, screen_name, group, node):
            """UserまたはGroupが許可されていないか確認します
            """
            return not cls.is_accepted(screen_name, node)

    def after_create(target, conn, **kw):
        try:
            DatabaseManager.start_session()
            for perm_ in permissions:
                perm = InnerPermission()
                perm.name = perm_["name"]
                perm.screen_name = perm_["screen_name"]
                db_.session.add(perm)
            db_.session.commit()
        except Exception as err:
            print(err)
            DatabaseManager.rollback_session()
        finally:
            DatabaseManager.close_session()

    event.listen(InnerPermission.__table__, "after_create", after_create)

    return InnerPermission
