#!/usr/bin/python

class Command:
    def handle(self, argv = None):
        print('usage: mitama <command> [<args>]')
        print('')
        print('new [name]       Create new Mitama project')
        print('init             Initialize directory as Mitama project')
        print('createapp [name] Create new Mitama application package')
        print('run [port]       Launch server in specified port')
        print('version          Show version of Mitama')
