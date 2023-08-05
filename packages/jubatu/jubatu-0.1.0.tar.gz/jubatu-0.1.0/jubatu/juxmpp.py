#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Xmpp communication module."""

import wx
import events
import pyxmpp
import pyxmpp.all
from pyxmpp.jabber.client import JabberClient
from pyxmpp.jabber.disco import DiscoInfo, DiscoIdentity, DiscoItems
import threading
import commands
import Queue
import time
import dns.resolver
import dns.exception
import socket
import copy
import logging
from pyxmpp.jabber import muc

JUBATU_PRIORITY = -16


class XmppClient(wx.EvtHandler, JabberClient):
    """Xmpp protocol manager.
    
    This class implements the xmpp client which manages all the xmpp protocol. Obviously, only one client is
    expected to be used. The interaction with game engines will work in both directions: games engines will ask it 
    to send the iq-stanzas corresponding to the game-specific protocol, and the incoming iq-stanzas will be
    redirected to the appropiate game engines for his processing (the game engines will be identified by their
    corresponding engine-id's).
    """
    
    def __init__(self, jid, password, server):
        wx.EvtHandler.__init__(self)
        JabberClient.__init__(self, jid, password, server, keepalive=30, disco_name=u'Jubatu', disco_category=u'client', disco_type=u'gaming')
        self.isDetached = False
        
        self.disco_info.add_feature("jubatu:games")

    def authorized(self):
        """Handle 'authorized' event
        
        The handlers for the different kinds of incoming messages are set here.
        """
        
        JabberClient.authorized(self)
        logging.getLogger("xmppComm").debug("'authorized' signal received")
        self.get_stream().set_presence_handler("", self.presence_available)
        self.get_stream().set_presence_handler("unavailable", self.presence_unavailable)
        self.get_stream().set_message_handler("chat", self.message_handler)
        self.get_stream().set_iq_set_handler("proposal", "jubatu:games", self.iq_set_handler)
        self.get_stream().set_iq_set_handler("turn", "jubatu:games", self.iq_set_handler)

    def disco_get_info(self, node, iq):
        """Return disco#info.
        
        Besides the basic configuration, it's added the identity for jubatu and the feature "jubatu:games"
        """
        
        logging.getLogger("xmppComm").debug("Request stanza:\n%s", iq.serialize())
        di = JabberClient.disco_get_info(self, node, iq)
            
        if node=="jubatu-engines":
            if di is None:
                di = DiscoInfo("jubatu-engines")  # we mirror the node in accordance with XEP-0030 3.2
                
        logging.getLogger("xmppComm").debug("Returned Disco#info:\n%s", di.xmlnode.serialize())
        return di

    def disco_get_items(self, node, iq):
        """Return disco#items.
        
        When the items for the jubatu-game-list node are required, we construct it. Otherwise, the basic info is
        returned.
        """
        
        logging.getLogger("xmppComm").debug("Request stanza:\n%s", iq.serialize())
        logging.getLogger("xmppComm").debug("Node queried: %s", node)
        
        if node is None:
            discoItems = JabberClient.disco_get_items(self, node, iq)
            discoItems.add_item(self.jid, "jubatu-engines")
        elif node=="jubatu-engines":
            discoItems = DiscoItems()
            for engine in wx.GetApp().engineDict.values():
                discoItems.add_item(self.jid, "jubatu-engines/"+engine.id())
        else:
            discoItems = JabberClient.disco_get_items(self, node, iq)
            
        logging.getLogger("xmppComm").debug("Returned disco#items:\n%s", discoItems.xmlnode.serialize())
        return discoItems

    def fix_out_stanza(self, stanza):
        """ Fixes outgoing stanzas.
        
        This is useful to filling info like stanzas's ids that isn't game protocol specific.
        """
        
        stanza.set_from(self.jid)
        if stanza.get_id() is None:
            stanza.set_id(self.get_stream().generate_id())
        logging.getLogger("xmppComm").debug("Fixed output stanza:\n%s", stanza.serialize())

    def connected(self):
        """Handle 'connected' event"""
        
        logging.getLogger("xmppComm").info("'connected' signal received")
        self.AddPendingEvent(events.JuConnected())

    def session_started(self):
        """Handle 'session started' event"""
        
        logging.getLogger("xmppComm").info("Session started")
        presence = pyxmpp.presence.Presence(priority=JUBATU_PRIORITY)
        self.get_stream().send(presence)
        self.request_roster()
        self.AddPendingEvent(events.JuSessionStarted())

    def disconnected(self):
        """Handle 'disconnected' event"""
        
        logging.getLogger("xmppComm").info("'disconnected' signal received")
        self.AddPendingEvent(events.JuDisconnected())

    def roster_updated(self, item=None):
        """Handle 'roster update' event"""
        
        if item==None:
            for rosterItem in self.roster.items_dict.values():
                self.AddPendingEvent(events.JuRosterItem(rosterItem))
        else:
            self.AddPendingEvent(events.JuRosterItem(item))

    def stream_closed(self, stream):
        """Handle 'stream closure' event."""
        
        logging.getLogger("xmppComm").debug("Stream closed")
        
    def stream_created(self, stream):
        """Handle 'stream creation' event."""
        
        logging.getLogger("xmppComm").debug("Stream created")

    def stream_error(self, err):
        """Handle the reception of a stream error."""
        
        logging.getLogger("xmppComm").error("Stream error: %s", err.get_message())

    def loop_iter(self, timeout=0):
        """Implements an iteration of the main loop of the client."""
        
        stream=self.get_stream()
        if not stream:
            return
        try:
            act=stream.loop_iter(timeout)
            if not act:
                self.idle()
        except pyxmpp.streamsasl.SASLAuthenticationFailed:
            logging.getLogger("xmppComm").debug("SASLAuthenticationFailed error")
            self.state_changed.acquire()
            try:
                try:
                    stream.close()
                except:
                    pass
            finally:
                self.stream = None
                self.state_changed.notify()
                self.state_changed.release()
                self.AddPendingEvent(events.JuSASLAuthenticationFailed())

    def presence_available(self, stanza):
        """Handle the reception of a presence stanza."""
        
        logging.getLogger("xmppComm").debug(stanza.serialize())
        self.AddPendingEvent(events.JuPresence(stanza))
        discoIq = pyxmpp.iq.Iq(None, self.jid, stanza.get_from(), "get", self.get_stream().generate_id())
        discoIq.new_query('http://jabber.org/protocol/disco#info')
        self.get_stream().set_response_handlers(discoIq, self.received_disco_info, self.iq_error)
        self.get_stream().send(discoIq)

    def presence_unavailable(self, stanza):
        """Handle the reception of a 'unavailable' presence stanza."""
        
        logging.getLogger("xmppComm").debug(stanza.serialize())
        self.AddPendingEvent(events.JuPresence(stanza))

    def message_handler(self, stanza):
        """Handle the reception of a user-readable message.
        
        As of now, the management of such messages is not implemented, but this could change in future versions.
        """
        
        logging.getLogger("xmppComm").debug(stanza.serialize())
        errorStanza = stanza.make_error_response("feature-not-implemented")
        #errorStanza = stanza.make_error_response("service-unavailable")
        self.get_stream().send(errorStanza)

    def iq_set_handler(self, stanza):
        """Handle the receipt of a iq stanza of type 'set'."""
        
        logging.getLogger("xmppComm").debug(stanza.serialize())
        payload = stanza.get_query()
        # send the stanza to the proper game engine
        logging.getLogger("xmppComm").debug("Game engine: %s", wx.GetApp().engineDict[payload.prop("engine-id")].name())
        wx.GetApp().engineDict[payload.prop("engine-id")].commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy()))
        
    def iq_error(self, stanza):
        """Handle the receipt of a iq error stanza."""
        
        logging.getLogger("xmppComm").error(stanza.serialize())

    def received_disco_info(self, stanza):
        """Handle the receipt of disco#info information."""
        
        logging.getLogger("xmppComm").debug(stanza.serialize())
        di = DiscoInfo(stanza.get_query())
        if di.has_feature("jubatu:games"):
            logging.getLogger("xmppComm").debug("'jubatu:games' feature detected")
            discoIq = pyxmpp.iq.Iq(None, self.jid, stanza.get_from(), "get", self.get_stream().generate_id())
            xmlNode = discoIq.new_query('http://jabber.org/protocol/disco#items')
            xmlNode.setProp("node", "jubatu-engines")
            self.get_stream().set_response_handlers(discoIq, self.received_disco_items, self.iq_error)
            self.get_stream().send(discoIq)
            
    def received_disco_items(self, stanza):
        """Handle the receipt of disco#items information."""
        
        logging.getLogger("xmppComm").debug(stanza.serialize())
        discoItems = DiscoItems(stanza.get_query())
        
        engineCollection = set()
        for item in discoItems.get_items():
            engineCollection.add(item.get_node().split('/')[-1])
            
        logging.getLogger("xmppComm").debug("Engine IDs: %s", engineCollection)
        self.AddPendingEvent(events.JuEngineList(stanza.get_from_jid(), engineCollection))
            
    def set_presence(self, showStatus):
        """Set the presence of the local user to a given status.
        
        showStatus -- 'show' status to be set for the local user.
        """
        
        presence = pyxmpp.presence.Presence(priority=JUBATU_PRIORITY, show=showStatus)
        logging.getLogger("xmppComm").debug(presence.serialize())
        self.get_stream().send(presence)

    def send_iq_stanza(self, iqStanza, res_handler, err_handler, timeout_handler, timeout):
        """ Send a iq stanza.
        
        iqStanza -- iq stanza to be send
        res_handler -- result handler to be set for a normal reply to the stanza.
        err_handler -- error handler to be set for an error replied to the stanza.
        timeout_handler -- timeout handler to be set for the stanza. Will be called when no answer of type 'result'
            or 'error' is received in a given time interval.
        timeout -- the interval, in seconds, after which the timeout_handler will be called.
        """
        
        logging.getLogger("xmppComm").debug(iqStanza.serialize())
        self.get_stream().set_response_handlers(iqStanza, res_handler, err_handler, timeout_handler, timeout)
        self.get_stream().send(iqStanza)

    def send_iq_stanza_reply(self, stanza):
        """Send a reply for a received stanza.
        
        stanza -- the reply stanza
        This work as a simplified version of 'send_iq_stanza'.
        """
        
        logging.getLogger("xmppComm").debug(stanza.serialize())
        self.get_stream().send(stanza)

    def open_muc(self):     # Experimental; do not use in engines.
        """Experimental. Do not use."""
        
        logging.getLogger("xmppComm").debug("Opening muc")
        room_manager = muc.MucRoomManager(self.get_stream())
        room_state = muc.MucRoomState(room_manager, self.jid, pyxmpp.JID("andy_test_room@conf.jabberes.org/andy"), muc.MucRoomHandler())
        room_manager.set_handlers()
        room_state.join()



class XmppClientThread(threading.Thread):
    """Thread managing the xmpp protocol.
    
    Only an object for this class is expected to be used, and it will be accesible program-wide as it will be contained
    in the main application class instance (wx.GetApp().xmppThread). This thread will contain the instance of XmppClient
    managing the protocol and a commands queue used to asynchonously receive command from other parts of the program.
    """
    
    xmppClient = None
    commandsQueue = Queue.Queue()
    __commandsQueue = []
    
    def __init__(self):
        logging.getLogger("xmppComm").setLevel(logging.WARNING)   # set the logging verbosity for this module here
        threading.Thread.__init__(self)

    def run(self):
        """Main loop for the thread.LockType
        
        Basicly, it iterate the 'xmppClient' object, check and process the received commands, and check
        the exit conditions.
        """
        
        while True:
            self.preprocess_commands()
            if len(self.__commandsQueue)>0:
                self.process_command(self.__commandsQueue.pop(0))
            if self.xmppClient!=None:
                self.xmppClient.loop_iter(1)
            time.sleep(0.1)
            # Exit condition.
            # wx seems to be None sometimes when the main window have been closed, so we have to check whether wx is None
            if len(self.__commandsQueue)==0 and (wx is None or not wx.GetApp().GetTopWindow()):
                return

    def preprocess_commands(self):
        """Preprocess the command list.
        
        This is primarily intended to allow to cancel some previous actions; take into account that some
        actions asked to the module can take a good amount of second before being complete (i.e., a connection)
        so it's probably a good idea to see if, after such wait, the user have issued another order and subsequently
        cancelled it.
        """
        
        try:
            while True:
                command = self.commandsQueue.get_nowait()
                if command.id==commands.JU_XMPP_CANCEL_CONNECT:
                    if len(self.__commandsQueue)>0:
                        assert(self.__commandsQueue[-1].id==commands.JU_XMPP_CONNECT)
                        self.__commandsQueue.pop(0)
                    else:
                        self.__commandsQueue.append(command)
                else:
                    self.__commandsQueue.append(command)
        except Queue.Empty:
            pass

    def process_command(self, command):
        """Process a received command, calling the appropiate handlers."""
        
        if command.id==commands.JU_XMPP_INITIALIZE:
            self.xmppClient = XmppClient(
                command.jid,
                command.password,
                command.server)
        elif command.id==commands.JU_XMPP_CONNECT:
            try:
                self.xmppClient.connect()
            except dns.exception.Timeout:
                logging.getLogger("xmppComm").error("dns.exception.Timeout error")
                wx.GetApp().AddPendingEvent(events.JuStatusMessageEvent(_("Timeout problem"), 5000))
                wx.GetApp().AddPendingEvent(events.JuDnsTimeout())
            except dns.resolver.NXDOMAIN:
                wx.GetApp().AddPendingEvent(events.JuStatusMessageEvent(_("NXDOMAIN problem"), 5000))
                wx.GetApp().AddPendingEvent(events.JuDnsDXDOMAIN())
            except socket.error, msg:
                logging.getLogger("xmppComm").error("Socket error")
                wx.GetApp().AddPendingEvent(events.JuStatusMessageEvent(_("Socket problem"), 5000))
                wx.GetApp().AddPendingEvent(events.JuSocketError())
        elif command.id==commands.JU_XMPP_CANCEL_CONNECT:
            if self.xmppClient != None:
                self.xmppClient.disconnect()
                self.xmppClient = None
        elif command.id==commands.JU_XMPP_DISCONNECT:
            self.xmppClient.disconnect()
        elif command.id==commands.JU_XMPP_SET_PRESENCE:
            self.xmppClient.set_presence(command.show)
        elif command.id==commands.JU_XMPP_SEND_IQ_STANZA:
            self.xmppClient.send_iq_stanza(command.stanza, command.res_handler, command.err_handler, command.timeout_handler, command.timeout)
        elif command.id==commands.JU_XMPP_SEND_IQ_STANZA_REPLY:
            self.xmppClient.send_iq_stanza_reply(command.stanza)
        elif command.id==commands.JU_XMPP_OPEN_MUC:
            self.xmppClient.open_muc()
        
