# -*- test-case-name: anymeta.xmpp.test.test_service -*-
#
# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

"""
anyMeta publish-subscribe services.
"""

import cgi
import simplejson
from time import gmtime, strftime

from twisted.internet import defer
from twisted.python import log
from twisted.web2 import http, http_headers, resource, responsecode
from twisted.web2.stream import readStream
from twisted.words.protocols.jabber.error import StanzaError
from twisted.words.protocols.jabber.jid import internJID as JID
from twisted.words.xish import domish

from wokkel import disco, pubsub
from wokkel.generic import parseXml

from anymeta.api.base import AnyMetaException

NS_ATOM = 'http://www.w3.org/2005/Atom'
MIME_ATOM_ENTRY = http_headers.MimeType('application',
                                        'atom+xml',
                                        {'type': 'entry',
                                         'charset': 'utf-8'})
MIME_JSON = http_headers.MimeType('application', 'json')

class Error(Exception):
    pass



class BadRequestError(Error):
    pass



class MissingMediaTypeError(Error):
    pass



class UnsupportedMediaTypeError(Error):
    pass



class ResourceNotLocal(Error):
    pass



class NodeNotFound(Error):
    """
    Node not found.
    """



class NotSubscribed(Error):
    """
    Entity is not subscribed to this node.
    """



class SubscriptionExists(Error):
    """
    There already exists a subscription to this node.
    """



class Forbidden(Error):
    pass



class XMPPURIParseError(ValueError):
    """
    Raised when a given XMPP URI couldn't be properly parsed.
    """



_excToHTTPStatusMap = {
        NodeNotFound:
            (responsecode.FORBIDDEN, "Node not found"),
        NotSubscribed:
            (responsecode.FORBIDDEN, "No such subscription found"),
        SubscriptionExists:
            (responsecode.FORBIDDEN, "Subscription already exists"),
        BadRequestError:
            (responsecode.BAD_REQUEST, "Bad request"),
        MissingMediaTypeError:
            (responsecode.BAD_REQUEST, "Media type not specified"),
        UnsupportedMediaTypeError:
            (responsecode.UNSUPPORTED_MEDIA_TYPE, "Unsupported media type"),
        XMPPURIParseError:
            (responsecode.BAD_REQUEST, "Malformed XMPP URI"),
        }



def excToHTTPStatus(failure):
    """
    Convert an exception to an appropriate HTTP status response.
    """
    e = failure.trap(*_excToHTTPStatusMap.keys())

    code, description = _excToHTTPStatusMap[e]

    msg = str(failure.value)

    if msg:
        description = "%s: %s" % (description, msg)
    return http.StatusResponse(code, description)



def getServiceAndNode(uri):
    """
    Given an XMPP URI, extract the publish subscribe service JID and node ID.
    """

    try:
        scheme, rest = uri.split(':', 1)
    except ValueError:
        raise XMPPURIParseError("No URI scheme component")

    if scheme != 'xmpp':
        raise XMPPURIParseError("Unknown URI scheme")

    if rest.startswith("//"):
        raise XMPPURIParseError("Unexpected URI authority component")

    try:
        entity, query = rest.split('?', 1)
    except ValueError:
        raise XMPPURIParseError("No URI query component")

    if not entity:
        raise XMPPURIParseError("Empty URI path component")

    try:
        service = JID(entity)
    except Exception, e:
        raise XMPPURIParseError("Invalid JID: %s" % e)

    params = cgi.parse_qs(query)

    try:
        nodeIdentifier = params['node'][0]
    except (KeyError, ValueError):
        nodeIdentifier = ''

    return service, nodeIdentifier



def getXMPPURI(service, nodeIdentifier):
    """
    Construct an XMPP URI from a service JID and node identifier.
    """
    return "xmpp:%s?;node=%s" % (service.full(), nodeIdentifier or '')



def extractAtomEntries(items):
    """
    Extract atom entries from a list of publish-subscribe items.

    @param items: List of L{domish.Element}s that represent publish-subscribe
                  items.
    @type items: C{list}
    """

    atomEntries = []

    for item in items:
        # ignore non-items (i.e. retractions)
        if item.name != 'item':
            continue

        atomEntry = None
        for element in item.elements():
            # extract the first element that is an atom entry
            if element.uri == NS_ATOM and element.name == 'entry':
                atomEntry = element
                break

        if atomEntry:
            atomEntries.append(atomEntry)

    return atomEntries



def constructFeed(service, nodeIdentifier, entries, title):
    nodeURI = getXMPPURI(service, nodeIdentifier)
    now = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())

    # Collect the received entries in a feed
    feed = domish.Element((NS_ATOM, 'feed'))
    feed.addElement('title', content=title)
    feed.addElement('id', content=nodeURI)
    feed.addElement('updated', content=now)

    for entry in entries:
        feed.addChild(entry)

    return feed



class WebStreamParser(object):
    def __init__(self):
        self.elementStream = domish.elementStream()
        self.elementStream.DocumentStartEvent = self.docStart
        self.elementStream.ElementEvent = self.elem
        self.elementStream.DocumentEndEvent = self.docEnd
        self.done = False


    def docStart(self, elem):
        self.document = elem


    def elem(self, elem):
        self.document.addChild(elem)


    def docEnd(self):
        self.done = True


    def parse(self, stream):
        def endOfStream(result):
            if not self.done:
                raise Exception("No more stuff?")
            else:
                return self.document

        d = readStream(stream, self.elementStream.parse)
        d.addCallback(endOfStream)
        return d



class AnyMetaPubSubAPI(object):
    """
    Abstraction of the services provided by the anyMeta PubSub module.

    @ivar apis: Mapping of domains to L{AnyMetaAPI} instances.
    @type apis: C{dict}
    """

    _errorMap = {
            'pubsub.subscribers.subscribe': {
                4: NodeNotFound,
                5: ResourceNotLocal,
                },
            'pubsub.subscribers.unsubscribe': {
                4: NodeNotFound,
                5: NotSubscribed,
                },
            }


    def __init__(self, apis):
        self.apis = apis


    def _mapErrors(self, failure, method):
        failure.trap(AnyMetaException)
        e = failure.value
        try:
            raise self._errorMap[method][e.code](str(e))
        except KeyError:
            if e.code == 99:
                raise Forbidden(str(e))
            else:
                raise Error(str(e))


    def getSubscribers(self, service, nodeIdentifier):
        """
        Get the subscribers to a node.

        @param service: JID of the service the node is located at.
        @type service: L{jid.JID}
        @param nodeIdentifier: Identifier of the node.
        @type: C{unicode}
        @return: Deferred that fires with a C{list} of L{jid.JID}s.
        @rtype: L{defer.Deferred}
        """

        def cb(result):
            for sub in result:
                if sub['status'] == 'subscribed':
                    yield JID('%s/%s' % (sub['jid_entity'],
                                         sub['jid_resource']))

        method = 'pubsub.subscribers.bynode'
        d = self.apis[service.host].doMethod(method, {'node': nodeIdentifier})
        d.addCallback(cb)
        d.addErrback(self._mapErrors, method)
        return d


    def getSubscriptions(self, service, entity):
        """
        Get the subscriptions for an entity.

        @param service: JID of the service the nodes are located at.
        @type service: L{jid.JID}
        @param entity: The entity to request the subscriptions for.
        @type entity: L{jid.JID}
        @return: Deferred that fires with a generator yielding
                 L{pubsub.Subscription}s.
        @rtype: L{defer.Deferred}
        """
        def cb(result):
            for sub in result:
                subscriber = JID('%s/%s' % (entity,
                                            sub['jid_resource']))
                yield pubsub.Subscription(sub['node'],
                                          subscriber,
                                          sub['status'])

        method = 'pubsub.subscribers.bysubscriber'
        d = self.apis[service.host].doMethod(method,
                                             {'jid_entity': entity.full()})
        d.addCallback(cb)
        d.addErrback(self._mapErrors, method)
        return d


    def subscribe(self, service, nodeIdentifier, subscriber):
        """
        Subscribe entity to a node.

        @return: A deferred that fires with the subscription state as
        L{pubsub.Subscription}.
        @rtype: L{defer.Deferred}
        """
        def cb(result):
            subscription = pubsub.Subscription(nodeIdentifier,
                                               subscriber,
                                               result['status'])

            subscription.new = result.get('created', False)
            return subscription

        method = 'pubsub.subscribers.subscribe'
        d = self.apis[service.host].doMethod(method,
                {'node': nodeIdentifier,
                 'jid_entity': subscriber.userhost(),
                 'jid_resource': subscriber.resource or ''})
        d.addCallback(cb)
        d.addErrback(self._mapErrors, method)
        return d


    def unsubscribe(self, service, nodeIdentifier, subscriber):
        """
        Unsubscribe an entity from a node.

        @return: A deferred that fires when unsubscription is complete.
        @rtype: L{defer.Deferred}
        """
        method = 'pubsub.subscribers.unsubscribe'
        d = self.apis[service.host].doMethod(method,
                {'node': nodeIdentifier,
                 'jid_entity': subscriber.userhost(),
                 'jid_resource': subscriber.resource or ''})
        d.addErrback(self._mapErrors, method)
        return d


    def items(self, service, nodeIdentifier):
        """
        Retrieve items published to a node.
        """
        def cb(data):
            payload = parseXml(data)
            return [pubsub.Item('current', payload)]

        method = 'pubsub.items'
        d = self.apis[service.host].doMethod(method,
                                             {'node': nodeIdentifier},
                                             format='atom')
        d.addCallback(cb)
        d.addErrback(self._mapErrors, method)
        return d


    def notify(self, recipient, service, nodeIdentifier,
                     payload, contentType, headers):
        method = 'pubsub.notify'
        nodeURI = getXMPPURI(service, nodeIdentifier)
        requestHeaders = {'Referer': nodeURI.encode('utf-8'),
                          'Content-Type': "%s;charset=utf-8" % contentType}

        if 'Collection' in headers:
            requestHeaders['Collection'] = ','.join(headers['Collection'])

        postdata = payload.toXml().encode('utf-8')
        d = self.apis[recipient.host].doMethod(method,
                {'uri': nodeURI},
                headers=requestHeaders,
                data=postdata)
        d.addErrback(self._mapErrors, method)
        d.addErrback(log.err)
        return d


    def delete(self, recipient, service, nodeIdentifier, redirectURI):
        print "In delete"
        print recipient, service, nodeIdentifier, redirectURI
        method = 'pubsub.notify'
        nodeURI = getXMPPURI(service, nodeIdentifier)
        requestHeaders = {'Referer': nodeURI.encode('utf-8'),
                          'Event': 'DELETED'}

        if redirectURI:
            requestHeaders['Link'] = \
                    '<%s>; rel=alternate' % redirectURI.encode('utf-8')

        d = self.apis[recipient.host].doMethod(method,
                {'uri': nodeURI},
                headers=requestHeaders,
                data=None)
        d.addErrback(self._mapErrors, method)
        d.addErrback(log.err)
        return d



class AnyMetaBackend(pubsub.PubSubResource):
    """
    Publish-subscribe backend to anyMeta.

    @ivar api: The anyMeta PubSub API.
    @type api: L{AnyMetaPubSubAPI}.
    """

    features = ["persistent-items",
                "retrieve_items",
                "retrieve_subscriptions",
                "subscribe",
                ]

    discoIdentity = disco.DiscoIdentity('pubsub', 'service',
                                        'anyMeta publish-subscribe service')

    pubsubService = None

    _errorMap = {
            NodeNotFound: ('item-not-found', None, None),
            ResourceNotLocal: ('feature-not-implemented',
                               'unsupported',
                               'subscribe'),
            NotSubscribed: ('unexpected-request', 'not-subscribed', None),
            }


    def __init__(self, api):
        self.api = api


    def _mapErrors(self, failure):
        e = failure.trap(*self._errorMap.keys())

        condition, pubsubCondition, feature = self._errorMap[e]
        try:
            msg = failure.value.msg
        except:
            msg = None

        if pubsubCondition:
            exc = pubsub.PubSubError(condition, pubsubCondition, feature, msg)
        else:
            exc = StanzaError(condition, text=msg)

        raise exc


    def subscribe(self, request):
        """
        Request the subscription of an entity to a pubsub node.

        @return: A deferred that fires with the subscription state as
                 L{pubsub.Subscription}.
        @rtype: L{defer.Deferred}
        """

        def notify(items, subscription):
            if not items:
                return

            notifications = [(request.subscriber, [subscription], items)]
            self.pubsubService.notifyPublish(request.recipient,
                                             request.nodeIdentifier,
                                             notifications)

        def checkNewSubscription(subscription):
            if (subscription.state == 'subscribed' and subscription.new):
                d = self.api.items(request.recipient, request.nodeIdentifier)
                d.addCallback(notify, subscription)
                d.addErrback(log.err)

            return subscription

        if request.subscriber.userhostJID() != request.sender.userhostJID():
            return defer.fail(Forbidden())

        d = self.api.subscribe(request.recipient, request.nodeIdentifier,
                               request.subscriber)
        d.addCallback(checkNewSubscription)
        d.addErrback(self._mapErrors)
        return d



    def unsubscribe(self, request):
        """
        Cancel the subscription of an entity to a pubsub node.

        @return: A deferred that fires when unsubscription is complete.
        @rtype: L{defer.Deferred}
        """
        if request.subscriber.userhostJID() != request.sender.userhostJID():
            return defer.fail(Forbidden())

        d = self.api.unsubscribe(request.recipient, request.nodeIdentifier,
                                    request.subscriber)
        d.addErrback(self._mapErrors)
        return d


    def subscriptions(self, request):
        """
        Get current subscriptions for an entity.

        @return: Deferred that fires with a generator yielding
                 L{pubsub.Subscription}s.
        @rtype: L{defer.Deferred}
        """
        entity = request.sender.userhostJID()
        d = self.api.getSubscriptions(request.recipient, entity)
        d.addErrback(self._mapErrors)
        return d


    def items(self, request):
        """
        Called upon an items request by a remote entity.
        """

        d = self.api.items(request.recipient, request.nodeIdentifier)
        d.addErrback(self._mapErrors)
        return d


    def notifyPublish(self, service, nodeIdentifier, subscriptions, items):
        """
        Send out notifications for items published to a node.

        @param service: JID of the service the node is located at.
        @type service: L{jid.JID}
        @param nodeIdentifier: Identifier of the node.
        @type: C{unicode}
        @rtype: L{defer.Deferred}
        """

        def createNotifications():
            for subscription in subscriptions:
                yield (subscription.subscriber,
                       [subscription],
                       items)

        self.pubsubService.notifyPublish(service,
                                         nodeIdentifier,
                                         createNotifications())


    def notifyDelete(self, service, nodeIdentifier, subscribers,
                           redirectURI=None):
        """
        Send out notifications for items published to a node.

        @param service: JID of the service the node is located at.
        @type service: L{jid.JID}
        @param nodeIdentifier: Identifier of the node.
        @type: C{unicode}
        @rtype: L{defer.Deferred}
        """

        self.pubsubService.notifyDelete(service,
                                        nodeIdentifier,
                                        subscribers,
                                        redirectURI)



def checkMime(request, mimeType):
    """
    Check the MIME type of the request.
    """
    ctype = request.headers.getHeader('content-type')

    if not ctype:
        raise MissingMediaTypeError()

    if ctype != mimeType:
        ctypeString = http_headers.generateContentType(ctype)
        raise UnsupportedMediaTypeError(ctypeString)

    return request



def loadJSONFromStream(request):
    """
    Load a JSON object from the stream of a web request.
    """
    content = []

    def loadJSON(content):
        try:
            return simplejson.loads(content)
        except Exception:
            log.err()
            raise BadRequestError("Passed document is not proper JSON")

    d = readStream(request.stream, content.append)
    d.addCallback(lambda _: ''.join((str(item) for item in content)))
    d.addCallback(loadJSON)
    return d


class NotifyPublishResource(resource.Resource):
    """
    A resource to publish to a publish-subscribe node.
    """

    def __init__(self, backend):
        self.backend = backend


    http_GET = None

    def http_POST(self, request):
        """
        Respond to a POST request to create a new item.
        """

        def subscriptionsFromDict(subscriptions, nodeIdentifier):
            for subscription in subscriptions:
                subscriber = JID("%s/%s" % (subscription['jid_entity'],
                                            subscription['jid_resource']))
                if 'node' in subscription:
                    node = subscription['node']
                else:
                    node = nodeIdentifier
                yield pubsub.Subscription(node,
                                          subscriber,
                                          subscription['status'])

        def createPubSubItems(items):
            for item in items:
                try:
                    content = item['payload']
                except KeyError:
                    payload = None
                else:
                    payload = parseXml(content.encode('utf-8'))

                itemIdentifier = item.get('id', 'current')
                yield pubsub.Item(itemIdentifier, payload)

        def doNotify(params):
            try:
                uri = params['uri']
            except KeyError:
                raise BadRequestError("Missing 'uri' parameter")
            else:
                service, nodeIdentifier = getServiceAndNode(uri)

            try:
                subscriptions = params['subscriptions']
            except KeyError:
                raise BadRequestError("Missing 'subscriptions' parameter")
            else:
                subscriptions = subscriptionsFromDict(subscriptions,
                                                      nodeIdentifier)

            try:
                items = params['items']
            except KeyError:
                raise BadRequestError("Missing 'items' parameter")
            else:
                items = list(createPubSubItems(items))

            return self.backend.notifyPublish(service, nodeIdentifier,
                                              subscriptions, items)

        d = defer.succeed(request)
        d.addCallback(checkMime, MIME_JSON)
        d.addCallback(loadJSONFromStream)
        d.addCallback(doNotify)
        d.addCallback(lambda _: http.Response(responsecode.NO_CONTENT))
        d.addErrback(excToHTTPStatus)
        return d



class NotifyDeleteResource(resource.Resource):
    """
    A resource to publish to a publish-subscribe node.
    """

    def __init__(self, backend):
        self.backend = backend


    http_GET = None

    def http_POST(self, request):
        """
        Respond to a POST request to create a new item.
        """

        def doNotify(params):
            try:
                uri = params['uri']
            except KeyError:
                raise BadRequestError("Missing 'uri' parameter")
            else:
                service, nodeIdentifier = getServiceAndNode(uri)

            try:
                subscriptions = params['subscriptions']
            except KeyError:
                raise BadRequestError("Missing 'subscriptions' parameter")
            else:
                subscriptions = (JID("%s/%s" % (subscription['jid_entity'],
                                                subscription['jid_resource']))
                                 for subscription in subscriptions)

            redirectURI = params.get('redirect_uri', None)

            return self.backend.notifyDelete(service, nodeIdentifier,
                                             subscriptions, redirectURI)

        d = defer.succeed(request)
        d.addCallback(checkMime, MIME_JSON)
        d.addCallback(loadJSONFromStream)
        d.addCallback(doNotify)
        d.addCallback(lambda _: http.Response(responsecode.NO_CONTENT))
        d.addErrback(excToHTTPStatus)
        return d



class AnyMetaPubSubClient(pubsub.PubSubClient):
    """
    Publish-subscribe client for anyMeta.

    Notifications are POSTed to with the received items in notifications.
    """

    def __init__(self, api):
        self.api = api


    def itemsReceived(self, event):
        """
        Fire up HTTP client to do callback
        """

        atomEntries = extractAtomEntries(event.items)

        # Don't notify if there are no atom entries
        if not atomEntries:
            return

        if len(atomEntries) == 1:
            contentType = 'application/atom+xml;type=entry'
            payload = atomEntries[0]
        else:
            contentType = 'application/atom+xml;type=feed'
            payload = constructFeed(event.sender,
                                            event.nodeIdentifier,
                                            atomEntries,
                                            title='Received item collection')

        self.api.notify(event.recipient, event.sender, event.nodeIdentifier,
                        payload, contentType, event.headers)


    def deleteReceived(self, event):
        """
        Fire up HTTP client to do callback
        """

        print "deleteReceived"
        print event.__dict__
        self.api.delete(event.recipient, event.sender, event.nodeIdentifier,
                        event.redirectURI)



class RemoteSubscribeBaseResource(resource.Resource):
    """
    Base resource for remote pubsub node subscription and unsubscription.

    This resource accepts POST request with a JSON document that holds a
    dictionary with the key C{uri} the XMPP URI of the publish-subscribe node.

    This class should be inherited with L{backendMethod} overridden.

    @cvar backendMethod: The name of the method to be called with
                         the JID of the pubsub service, the node identifier
                         and the callback URI as received in the HTTP POST
                         request to this resource.
    """
    clientMethod = None

    def __init__(self, client):
        self.client = client


    http_GET = None


    def http_POST(self, request):

        def gotRequest(params):
            subscriber = JID(params['subscriber'])
            uri = params['uri']

            service, nodeIdentifier = getServiceAndNode(uri)
            method = getattr(self.client, self.clientMethod)
            d = method(service, nodeIdentifier, subscriber, sender=subscriber)
            return d

        d = defer.succeed(request)
        d.addCallback(checkMime, MIME_JSON)
        d.addCallback(loadJSONFromStream)
        d.addCallback(gotRequest)
        d.addCallback(lambda _: http.Response(responsecode.NO_CONTENT))
        d.addErrback(excToHTTPStatus)
        return d



class RemoteSubscribeResource(RemoteSubscribeBaseResource):
    """
    Resource to subscribe to a remote publish-subscribe node.
    """
    clientMethod = 'subscribe'



class RemoteUnsubscribeResource(RemoteSubscribeBaseResource):
    """
    Resource to unsubscribe from a remote publish-subscribe node.
    """
    clientMethod = 'unsubscribe'



class RemoteItemsResource(resource.Resource):
    """
    Resource for retrieving items from a remote pubsub node.
    """

    def __init__(self, client):
        self.client = client


    def render(self, request):
        try:
            maxItems = int(request.args.get('max_items', [0])[0]) or None
        except ValueError:
            return http.StatusResponse(responsecode.BAD_REQUEST,
                    "The argument max_items has an invalid value.")

        try:
            uri = request.args['uri'][0]
        except KeyError:
            return http.StatusResponse(responsecode.BAD_REQUEST,
                    "No URI for the remote node provided.")

        try:
            subscriber = JID(request.args['subscriber'][0])
        except KeyError:
            return http.StatusResponse(responsecode.BAD_REQUEST,
                    "No URI for the remote node provided.")

        try:
            service, nodeIdentifier = getServiceAndNode(uri)
        except XMPPURIParseError:
            return http.StatusResponse(responsecode.BAD_REQUEST,
                    "Malformed XMPP URI: %s" % uri)

        def respond(items):
            """Create a feed out the retrieved items."""
            contentType = http_headers.MimeType('application',
                                                'atom+xml',
                                                {'type': 'feed'})
            atomEntries = extractAtomEntries(items)
            feed = constructFeed(service, nodeIdentifier, atomEntries,
                                    "Retrieved item collection")
            payload = feed.toXml().encode('utf-8')
            return http.Response(responsecode.OK, stream=payload,
                                 headers={'Content-Type': contentType})

        def trapNotFound(failure):
            failure.trap(StanzaError)
            if not failure.value.condition == 'item-not-found':
                raise failure
            return http.StatusResponse(responsecode.NOT_FOUND,
                                       "Node not found")

        d = self.client.items(service, nodeIdentifier, maxItems,
                              sender=subscriber)
        d.addCallback(respond)
        d.addErrback(trapNotFound)
        return d
