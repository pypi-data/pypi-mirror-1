# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import sys
import xmlrpclib


def main(server):
    _, command, resource, client = sys.argv
    assert command in ['lock', 'unlock']

    s = xmlrpclib.Server(server)
    function = getattr(s, command)
    function(resource, client)
