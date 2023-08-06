##############################################################################
#
# Copyright (c) 2005 Chris McDonough
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZConfig datatype support for ClockServer """

from ZServer.datatypes import ServerFactory

class ClockServerFactory(ServerFactory):
    def __init__(self, section):
        ServerFactory.__init__(self)
        self.method = section.method
        self.period = section.period
        self.user = section.user
        self.password = section.password
        self.host = ''
        self.section_host = section.host

    def create(self):
        from Products.ClockServer.ClockServer import ClockServer
        from ZServer.AccessLogger import access_logger
        return ClockServer(self.method, self.period, self.user,
                           self.password, self.section_host, access_logger)
    
