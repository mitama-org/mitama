from mitama._extra import _Singleton

class HookRegistry(_Singleton):
    def __init__(self):
        self.create_user_hooks = list()
        self.create_group_hooks = list()
        self.update_user_hooks = list()
        self.update_group_hooks = list()
        self.delete_user_hooks = list()
        self.delete_group_hooks = list()
    def create_user(self, target):
        for func in self.create_user_hooks:
            func(target)
    def create_group(self, target):
        for func in self.create_group_hooks:
            func(target)
    def update_user(self, target):
        for func in self.update_user_hooks:
            func(target)
    def update_group(self, target):
        for func in self.update_group_hooks:
            func(target)
    def delete_user(self, target):
        for func in self.delete_user_hooks:
            func(target)
    def delete_group(self, target):
        for func in self.delete_group_hooks:
            func(target)
    def add_create_user_hook(self, func):
        self.create_user_hooks.append(func)
    def add_create_group_hook(self, func):
        self.create_group_hooks.append(func)
    def add_update_user_hook(self, func):
        self.update_user_hooks.append(func)
    def add_update_group_hook(self, func):
        self.update_group_hooks.append(func)
    def add_delete_user_hook(self, func):
        self.delete_user_hooks.append(func)
    def add_delete_group_hook(self, func):
        self.delete_group_hooks.append(func)
