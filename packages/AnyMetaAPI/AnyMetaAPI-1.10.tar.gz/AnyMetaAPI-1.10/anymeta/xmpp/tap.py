# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

from ConfigParser import ConfigParser

from twisted.application import service, strports
from twisted.python import usage
from twisted.web2 import channel, log, resource, server
from twisted.web2.tap import Web2Service

from wokkel.component import InternalComponent, Router
from wokkel.disco import DiscoHandler
from wokkel.generic import FallbackHandler, VersionHandler
from wokkel.pubsub import PubSubService
from wokkel.server import ServerService, XMPPS2SServerFactory

from anymeta import manhole
from anymeta.api.base import AnyMetaAPI
from anymeta.xmpp import service as anyservice

__version__ = '0.0.1'

class Options(usage.Options):
    optParameters = [
            ('port', None, '5269', 'Server-to-server port'),
            ('config', 'c', '~/.anyxmpp.conf', 'Configuration file'),
            ('webport', None, '8088', 'Web port'),
            ('manhole-port', None, 'tcp:2224:interface=127.0.0.1',
                                   'Manhole port'),
    ]

    optFlags = [
        ('verbose', 'v', 'Show traffic'),
    ]

    def postOptions(self):
        import os
        parser = ConfigParser()
        cfgfile = os.path.expanduser(self['config'])
        if not os.path.exists(cfgfile):
            raise Exception("Missing configuration file: %s " % cfgfile)
        parser.read(cfgfile)
        self['config'] = parser


def makeService(config):
    s = service.MultiService()

    # Set up anyMeta service

    apis = {}
    domains = set()
    for domain in config['config'].sections():
        domains.add(domain)
        entry = config['config'].get(domain, 'api_key')
        engine = 'twisted'
        apis[domain] = AnyMetaAPI.from_registry(entry, engine=engine)
    api = anyservice.AnyMetaPubSubAPI(apis)


    # Set up XMPP server

    router = Router()

    serverService = ServerService(router)
    if config["verbose"]:
        serverService.logTraffic = True

    s2sFactory = XMPPS2SServerFactory(serverService)
    if config["verbose"]:
        s2sFactory.logTraffic = True

    s2sService = strports.service(config['port'], s2sFactory)
    s2sService.setServiceParent(s)

    # Set up XMPP server-side component

    cs = InternalComponent(router)
    cs.setName('component')
    cs.setServiceParent(s)

    if config["verbose"]:
        cs.logTraffic = True

    FallbackHandler().setHandlerParent(cs)
    VersionHandler('anyXMPP', __version__).setHandlerParent(cs)
    DiscoHandler().setHandlerParent(cs)

    # Set up domains

    for domain in domains:
        serverService.domains.add(domain)
        cs.domains.add(domain)

    # Hook up XMPP Publish-subscribe service adaptor to the backend

    bs = anyservice.AnyMetaBackend(api)
    ps = PubSubService(bs)
    ps.setHandlerParent(cs)
    bs.pubsubService = ps

    # Hook up XMPP Publish-subscribe client adaptor to the backend

    pc = anyservice.AnyMetaPubSubClient(api)
    pc.setHandlerParent(cs)

    # Set up web service

    root = resource.Resource()

    # Set up resources that exposes the backend
    root.child_notify = anyservice.NotifyPublishResource(bs)
    root.child_delete = anyservice.NotifyDeleteResource(bs)

    # Set up resources for accessing remote pubsub nodes.
    root.child_subscribe = anyservice.RemoteSubscribeResource(pc)
    root.child_unsubscribe = anyservice.RemoteUnsubscribeResource(pc)
    root.child_items = anyservice.RemoteItemsResource(pc)

    if config["verbose"]:
        root = log.LogWrapperResource(root)

    site = server.Site(root)
    w = strports.service(config['webport'], channel.HTTPFactory(site))

    if config["verbose"]:
        logObserver = log.DefaultCommonAccessLoggingObserver()
        w2s = Web2Service(logObserver)
        w.setServiceParent(w2s)
        w = w2s

    w.setServiceParent(s)

    # Set up a manhole

    namespace = {'service': s,
                 'component': cs,
                 'backend': bs,
                 'site': site,
                 'webService': w,
                 'root': root}

    manholeFactory = manhole.getFactory(namespace, admin='admin')
    manholeService = strports.service(config['manhole-port'], manholeFactory)
    manholeService.setServiceParent(s)

    return s
