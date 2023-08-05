import logging
logger = logging.getLogger(__name__)

import datetime
from osaf import sharing, pim, startup
from osaf.pim.calendar.TimeZone import convertToICUtzinfo
from application import schema, Globals
from application.dialogs.AccountPreferences import AccountPanel
from twisted.words.protocols.jabber import client as jabberclient, jid
from twisted.internet import reactor
from twisted.words.xish import domish
from osaf.framework.certstore import ssl
from osaf.framework.twisted import waitForDeferred
from i18n import MessageFactory
_ = MessageFactory("Chandler-TwitterPlugin")

import logging
logger = logging.getLogger(__name__)


def installParcel(parcel, oldVersion=None):

    XMPPTask.update(parcel, "xmppTask",
        invoke="chandler_xmpp.XMPPJob",
        run_at_startup=True,
        active=True,
        interval=datetime.timedelta(minutes=1)
    )

    AccountPanel.update(parcel, "XMPPAccountPanel",
        accountClass = XMPPAccount,
        key = "SHARING_XMPP",
        info = {
            "fields" : {
                "XMPPSHARING_DESCRIPTION" : {
                    "attr" : "displayName",
                    "type" : "string",
                    "required" : True,
                    "default": _(u"New XMPP Account"),
                },
                "XMPPSHARING_USERNAME" : {
                    "attr" : "username",
                    "type" : "string",
                },
                "XMPPSHARING_PASSWORD" : {
                    "attr" : "password",
                    "type" : "password",
                },
                "XMPPSHARING_HOST" : {
                    "attr" : "host",
                    "type" : "string",
                },
                "XMPPSHARING_RESOURCE" : {
                    "attr" : "resource",
                    "type" : "string",
                },
                "XMPPSHARING_PORT" : {
                    "attr" : "port",
                    "type" : "integer",
                    "default" : 5222,
                },
                "XMPPSHARING_USE_SSL" : {
                    "attr" : "useSSL",
                    "type" : "boolean",
                    "linkedTo" :
                        ("XMPPSHARING_PORT", { True:"5222", False:"5222" }),
                },
            },
            "id" : "XMPPSHARINGPanel",
            "order": 100, # after OOTB accounts
            "displayName" : "XMPPSHARING_DESCRIPTION",
            "description" : _(u"XMPP / Jabber"),
            "protocol" : "XMPP",
        },
        xrc = """<?xml version="1.0" encoding="ISO-8859-15"?>
<resource>
  <object class="wxPanel" name="XMPPSHARINGPanel">
    <object class="wxBoxSizer">
      <orient>wxVERTICAL</orient>
      <object class="sizeritem">
        <flag>wxALIGN_CENTER|wxALL</flag>
        <border>5</border>
        <object class="wxFlexGridSizer">
          <cols>2</cols>
          <rows>0</rows>
          <vgap>0</vgap>
          <hgap>0</hgap>
          <object class="sizeritem">
            <flag>wxALIGN_RIGHT|wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <style>wxALIGN_RIGHT</style>
              <label>Account type:</label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <size>300,-1</size>
              <label>XMPP / Jabber</label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_RIGHT|wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <style>wxALIGN_RIGHT</style>
              <label>Descr&amp;iption:</label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxTextCtrl" name="XMPPSHARING_DESCRIPTION">
              <size>300,-1</size>
              <value></value>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_RIGHT|wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <style>wxALIGN_RIGHT</style>
              <label>User &amp;name:</label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxTextCtrl" name="XMPPSHARING_USERNAME">
              <size>300,-1</size>
              <value></value>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_RIGHT|wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <style>wxALIGN_RIGHT</style>
              <label>Pass&amp;word:</label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxTextCtrl" name="XMPPSHARING_PASSWORD">
              <size>300,-1</size>
              <style>wxTE_PASSWORD</style>
              <value></value>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_RIGHT|wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <style>wxALIGN_RIGHT</style>
              <label>&amp;Server:</label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxTextCtrl" name="XMPPSHARING_HOST">
              <size>300,-1</size>
              <value></value>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_RIGHT|wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <style>wxALIGN_RIGHT</style>
              <label>&amp;Resource:</label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxTextCtrl" name="XMPPSHARING_RESOURCE">
              <size>300,-1</size>
              <value></value>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_RIGHT|wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <border>5</border>
            <object class="wxStaticText" name="ID_TEXT">
              <style>wxALIGN_RIGHT</style>
              <label></label>
            </object>
          </object>
          <object class="sizeritem">
            <flag>wxALIGN_CENTER_VERTICAL|wxALL</flag>
            <object class="wxBoxSizer">
              <orient>wxHORIZONTAL</orient>
              <object class="sizeritem">
                <flag>wxALIGN_CENTER|wxALL</flag>
                <border>5</border>
                <object class="wxTextCtrl" name="XMPPSHARING_PORT">
                  <size>60,-1</size>
                  <value></value>
                </object>
              </object>
              <object class="sizeritem">
                <flag>wxALIGN_CENTER|wxALL</flag>
                <border>5</border>
                <object class="wxCheckBox" name="XMPPSHARING_USE_SSL">
                  <label>Use SSL</label>
                </object>
              </object>
            </object>
          </object>
        </object>
      </object>
    </object>
  </object>
</resource>
"""
    )


class XMPPJob(object):
    def __init__(self, item):
        self.rv = item.itsView

    def run(self, *args, **kwds):
        if Globals.options.offline:
            return True

        self.rv.refresh()
        uuids = [account.itsUUID for account in XMPPAccount.iterItems(self.rv)]
        for uuid in uuids:
            account = self.rv.findUUID(uuid)
            if account is not None:
                if not getattr(account, 'connected', False):
                    account.connect()
                else:
                    account.ping()
        return True



class XMPPTask(startup.PeriodicTask):
    def fork(self):
        return startup.fork_item(self, name='XMPPStartup', pruneSize=500,
            notify=False, mergeFn=sharing.mergeFunction)



class XMPPAccount(sharing.SharingAccount):
    accountProtocol = schema.One(initialValue = 'XMPP')
    accountType = schema.One(initialValue = 'SHARING_XMPP')
    connectAtStartup = schema.One(schema.Boolean, defaultValue=True)
    resource = schema.One(schema.Text, defaultValue="")

    def publish(self, collection, activity=None, filters=None, overwrite=False):
        # Not implemented
        raise sharing.SharingError("Publishing to XMPP not yet supported")


    def connect(self):

        self.connected = False

        if "@" in self.username:
            # gmail requires an id of user@gmail.com, but real hostname of
            # talk.google.com, so allow user to include the fake host as part
            # of the username
            id = self.username
        else:
            id = "%s@%s" % (self.username, self.host)

        id = "%s/%s" % (id, self.resource or "chandler")
        logger.info("Connecting to XMPP: %s", id)

        password = waitForDeferred(self.password.decryptPassword())

        self.id = jid.JID(id)

        factory = jabberclient.basicClientFactory(self.id, password)

        factory.addBootstrap('//event/stream/authd',
                             self.on_authd)
        factory.addBootstrap("//event/client/basicauth/authfailed",
                             self.on_authfailed)
        factory.addBootstrap("//event/client/basicauth/invaliduser",
                             self.on_invaliduser)
        factory.addBootstrap("//event/stream/error",
                             self.on_error)
        factory.addBootstrap("/*",
                             self.on_anything)

        if self.useSSL:
            ssl.connectSSL(self.host, self.port, factory, self.itsView)
        else:
            reactor.connectTCP(self.host, self.port, factory)


    def ping(self):
        logger.info("Sending XMPP ping: %s", self.id.full())
        presence = domish.Element(('jabber:client', 'presence'))
        self.xmlstream.send(presence)


    # def register(self, path, method):
    #     self.observers.append((path, method))
    #     self.xmlstream.addObserver(path, method)

    def on_authd(self, xmlstream):
        logger.info("XMPP authorization succesful: %s", self.id.full())

        self.xmlstream = xmlstream
        self.ping()
        xmlstream.addObserver('/message', self.on_message)
        xmlstream.addObserver('/presence', self.on_presence)
        xmlstream.addObserver('/iq', self.on_iq)
        self.connected = True


    def on_authfailed(self, elem):
        try:
            logger.error("XMPP authfailed: %s", elem.toXml().encode('utf-8'))
        except Exception, e:
            logger.exception("XMPP authfailed, couldn't read elem")

    def on_invaliduser(self, elem):
        try:
            logger.error("XMPP invaliduser: %s", elem.toXml().encode('utf-8'))
        except Exception, e:
            logger.exception("XMPP invaliduser, couldn't read elem")

    def on_error(self, elem):
        try:
            logger.error("XMPP error: %s", elem.toXml().encode('utf-8'))
        except Exception, e:
            logger.exception("XMPP Error, couldn't read elem")

    def on_anything(self, elem):
        try:
            logger.info("XMPP message: %s", elem.toXml().encode('utf-8'))
        except Exception, e:
            logger.exception("XMPP message, couldn't read elem")
        pass


    # TODO:
    # use endpoints to allow plugins to register to handle incoming messages,
    # subscribes, iqs, etc.  For now, they are hardcoded here:

    def on_message(self, elem):

        process_message(self.itsView, elem)

        try:
            # print "MESSAGE: %s" %(elem.toXml().encode('utf-8'))
            for child in elem.children:
                # print "-", child.uri, child.name
                if child.uri == 'jabber:client' and child.name == 'body':
                    body = unicode(child)
                    logger.info("XMPP Message: %s", body)
                if child.uri == 'http://jabber.org/protocol/chatstates':
                    logger.info("XMPP chatstate: %s", child.name)
        except:
            pass


    def on_presence(self, elem):
        # print "PRESENCE: %s" %(elem.toXml().encode('utf-8'))

        type = elem.attributes.get('type')
        # actually type is optional, and if it's missing that means available

        if type == 'subscribe':
            presence = domish.Element(('jabber:client', 'presence'))
            presence['to'] = elem['from']
            presence['type'] = 'subscribed'
            self.xmlstream.send(presence)
            logger.info("XMPP subscribe: %s", elem['from'])

        elif type == 'unsubscribe':
            presence = domish.Element(('jabber:client', 'presence'))
            presence['to'] = elem['from']
            presence['type'] = 'unsubscribed'
            self.xmlstream.send(presence)
            logger.info("XMPP unsubscribe: %s", elem['from'])

        else:
            for child in elem.children:
                if child.uri == 'jabber:client' and child.name == 'show':
                    value = str(child)
                    if value == "chat":
                        msg = "%s is looking to chat" % elem['from']
                    else:
                        msg = "%s is away" % elem['from']
                    break
            else:
                msg = "%s is available" % elem['from']

            logger.info("XMPP presence: %s", msg)


    def on_iq(self, elem):
        try:
            logger.info("XMPP iq: %s", elem.toXml().encode('utf-8'))
        except Exception, e:
            logger.exception("XMPP iq, couldn't read elem")



    def send_message(self, to, body):

        message = domish.Element(('jabber:client', 'message'))
        message['to'] = to
        message['type'] = 'chat'

        message.addElement('body', None, body)

        self.xmlstream.send(message)
        logger.info("XMPP sending: %s", message)





# Creates an event for each inbound XMPP message
def process_message(rv, elem):

    rv = get_view(rv.repository)

    body = ""
    screenname = ""
    for child in elem.children:
        # print "-", child.uri, child.name
        if child.uri == 'jabber:client' and child.name == 'body':
            body = unicode(child)
        if (child.uri == 'http://twitter.com/xmpp' and
            child.name == 'screenname'):
            screenname = unicode(child)

    if not body:
        return

    now = convertToICUtzinfo(rv,
        datetime.datetime.now()).astimezone(rv.tzinfo.default)

    # Create an event
    event = pim.CalendarEvent(itsView=rv,
        displayName = body,
        body = body,
        startTime = now,
        duration = datetime.timedelta(minutes=30),
        anyTime = False,
        transparency = 'fyi'
    )
    get_collection(rv).add(event.itsItem)
    rv.commit()



def get_collection(rv):
    # for now, just look for a collection named "XMPP"
    for collection in pim.SmartCollection.iterItems(rv):
        if collection.displayName == "XMPP":
            return collection
    collection = pim.SmartCollection(itsView=rv, displayName="XMPP")
    schema.ns('osaf.app', rv).sidebarCollection.add(collection)
    return collection


def get_view(repo):
    for view in repo.views:
        if view.name == "XMPP":
            return view
    return repo.createView("XMPP")


"""
Twitter inbound message:

<message xmlns='jabber:client' to='morgen@gmail.com' from='twitter@twitter.com' type='chat'><body>bear: @morgen don't think so</body><screen_name xmlns:twitter='http://twitter.com/xmpp'>bear</screen_name><profile_image xmlns:twitter='http://twitter.com/xmpp'>http://s3.amazonaws.com/twitter_production/profile_images/15013142/bear2_normal.jpg</profile_image></message>

Jaiku:
<message xmlns='jabber:client' type='chat' from='jaiku@jaiku.com/bot' to='morgen@gmail.com'><body>bear (to morgen): yea - it's an oddity (on yes I do)
Link: http://morgen.jaiku.com/presence/14843301</body><html xmlns='http://jabber.org/protocol/xhtml-im'><body xmlns='http://www.w3.org/1999/xhtml'><p>bear (to morgen): yea - it's an oddity (on <a href='http://morgen.jaiku.com/presence/14843301'>yes I do</a>)</p></body></html></message>

"""


# Export/reload

class XMPPAccountRecord(sharing.Record):
    URI = "http://osafoundation.org/eim/chandler_xmpp/account/0"
    uuid = sharing.key(sharing.ItemRecord.uuid)
    resource = sharing.field(sharing.TextType(size=1024))

class XMPPTranslator(sharing.Translator):
    URI = "cid:xmpp-translator@osaf.us"
    version = 1
    description = u"Translator for XMPP plugin"

    @XMPPAccountRecord.importer
    def import_account(self, record):
        self.withItemForUUID(record.uuid, XMPPAccount,
            resource=record.resource
        )

    @sharing.exporter(XMPPAccount)
    def export_account(self, account):
        yield XMPPAccountRecord(account, account.resource)
