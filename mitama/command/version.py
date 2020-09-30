#!/usr/bin/python

import pkg_resources

class Command:
    def handle(self, argv = None):
        v = pkg_resources.get_distribution('mitama').version
        print(v)
