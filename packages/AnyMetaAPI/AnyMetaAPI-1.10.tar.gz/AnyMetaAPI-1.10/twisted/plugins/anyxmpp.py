# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

from twisted.application.service import ServiceMaker

Idavoll = ServiceMaker(
        "anyXMPP",
        "anymeta.xmpp.tap",
        "anyMeta Publish-Subscribe Service Component",
        "anyxmpp")
