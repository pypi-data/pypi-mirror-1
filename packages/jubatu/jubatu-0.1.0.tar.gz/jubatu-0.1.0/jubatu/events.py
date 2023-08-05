import wx
import copy
import pyxmpp.all

wxEVT_STATUS_MESSAGE = wx.NewEventType()
EVT_STATUS_MESSAGE = wx.PyEventBinder(wxEVT_STATUS_MESSAGE)

wxEVT_SESSION_STARTED = wx.NewEventType()
EVT_SESSION_STARTED = wx.PyEventBinder(wxEVT_SESSION_STARTED)

wxEVT_CONNECTED = wx.NewEventType()
EVT_CONNECTED = wx.PyEventBinder(wxEVT_CONNECTED)

wxEVT_DISCONNECTED = wx.NewEventType()
EVT_DISCONNECTED = wx.PyEventBinder(wxEVT_DISCONNECTED)

wxEVT_SASL_AUTHENTICATION_FAILED = wx.NewEventType()
EVT_SASL_AUTHENTICATION_FAILED = wx.PyEventBinder(wxEVT_SASL_AUTHENTICATION_FAILED)

wxEVT_DNS_DXDOMAIN = wx.NewEventType()
EVT_DNS_DXDOMAIN = wx.PyEventBinder(wxEVT_DNS_DXDOMAIN)

wxEVT_DNS_TIMEOUT = wx.NewEventType()
EVT_DNS_TIMEOUT = wx.PyEventBinder(wxEVT_DNS_TIMEOUT)

wxEVT_SOCKET_ERROR = wx.NewEventType()
EVT_SOCKET_ERROR = wx.PyEventBinder(wxEVT_SOCKET_ERROR)

wxEVT_PRESENCE = wx.NewEventType()
EVT_PRESENCE = wx.PyEventBinder(wxEVT_PRESENCE)

wxEVT_PRESENCE_UNAVAILABLE = wx.NewEventType()
EVT_PRESENCE_UNAVAILABLE = wx.PyEventBinder(wxEVT_PRESENCE_UNAVAILABLE)

wxEVT_ROSTER_ITEM = wx.NewEventType()
EVT_ROSTER_ITEM = wx.PyEventBinder(wxEVT_ROSTER_ITEM)

wxEVT_ENGINE_LIST = wx.NewEventType()
EVT_ENGINE_LIST = wx.PyEventBinder(wxEVT_ENGINE_LIST)

wxEVT_CLOSE_CURRENT_TAB = wx.NewEventType()
EVT_CLOSE_CURRENT_TAB = wx.PyEventBinder(wxEVT_CLOSE_CURRENT_TAB)

wxEVT_BUDDY_SELECTED = wx.NewEventType()
EVT_BUDDY_SELECTED = wx.PyEventBinder(wxEVT_BUDDY_SELECTED)

wxEVT_MESSAGE_BOX = wx.NewEventType()
EVT_MESSAGE_BOX = wx.PyEventBinder(wxEVT_MESSAGE_BOX)


class JuStatusMessageEvent(wx.PyCommandEvent):
    """Event to ask a message to be displayed in the statusbar"""
    
    def __init__(self, message, timeout=0):  # timeout in milliseconds
        wx.PyCommandEvent.__init__(self, wxEVT_STATUS_MESSAGE)
        self.message = message
        self.timeout = timeout
        
class JuSessionStarted(wx.PyCommandEvent):
    """Event to signal the xmpp session start"""
    
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_SESSION_STARTED)
        
class JuConnected(wx.PyCommandEvent):
    """Event to signal the stablishment of the xmpp connection"""
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_CONNECTED)
        
class JuDisconnected(wx.PyCommandEvent):
    """Event to signal the xmpp session disconnection"""
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_DISCONNECTED)
        
class JuSASLAuthenticationFailed(wx.PyCommandEvent):
    """Event to signal a SASL authentication error"""
    
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_SASL_AUTHENTICATION_FAILED)

class JuDnsDXDOMAIN(wx.PyCommandEvent):
    """Event to signal a DNS domain error"""
    
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_DNS_DXDOMAIN)

class JuDnsTimeout(wx.PyCommandEvent):
    """Event to signal a DNS timeout"""
    
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_DNS_TIMEOUT)
        
class JuSocketError(wx.PyCommandEvent):
    """Event to signal a socket error"""
    
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_SOCKET_ERROR)
        
##class JuPresenceInfo(wx.PyCommandEvent):
##    """Event to ask setting a new status for the user's xmpp presence"""
##
##    def __init__(self, code):
##        wx.PyCommandEvent.__init__(self, code)
    
class JuPresence(wx.PyCommandEvent):
    """Event to signal the receipt of a 'presence available' stanza"""
    
    def __init__(self, stanza):
        wx.PyCommandEvent.__init__(self, wxEVT_PRESENCE)
        self.stanza = stanza.copy()

#class JuPresenceUnavailable(JuPresenceInfo):
class JuPresenceUnavailable(wx.PyCommandEvent):
    """Event to signal the receipt of a 'presence unavailable' stanza"""
    
    def __init__(self, presenceUnavailableStanza):
        #JuPresenceInfo.__init__(self, wxEVT_PRESENCE_UNAVAILABLE)
        wx.PyCommandEvent.__init__(self, wxEVT_PRESENCE_UNAVAILABLE)

class JuRosterItem(wx.PyCommandEvent):
    """Event to signal the receipt of a roster item"""
    
    def __init__(self, rosterItem):
        wx.PyCommandEvent.__init__(self, wxEVT_ROSTER_ITEM)
        self.rosterItem = rosterItem
        
class JuEngineList(wx.PyCommandEvent):
    """Event to signal the receipt of the list of engines of a buddy through 'Service Discovery' (XEP-0030)"""
    
    def __init__(self, jid, engineList):
        wx.PyCommandEvent.__init__(self, wxEVT_ENGINE_LIST)
        self.jid = jid
        self.engineList = engineList
        
class JuCloseCurrentTab(wx.PyCommandEvent):
    """Auxiliar event for a tab to ask his closing to his parent notebook"""
    
    def __init__(self):
        wx.PyCommandEvent.__init__(self, wxEVT_CLOSE_CURRENT_TAB)

class JuBuddySelected(wx.PyEvent):
    """Event to signal the selection of a buddy from a buddy list
    
    This is intended to simplify the work of game modules' programmers. Once focused a given list with the
    participants in the game, you only have to wait the receipt of a JuBuddySelected events till
    filling the list.
    """
    
    def __init__(self, jid, control=None):
        wx.PyEvent.__init__(self, eventType=wxEVT_BUDDY_SELECTED)
        self.jid = jid
        self.control = control

class JuMessageBox(wx.PyCommandEvent):
    """Event to ask the showing of a message box to the user."""
    
    def __init__(self, message, caption, style, commandQueue=None, returnObject=None):
        wx.PyCommandEvent.__init__(self, eventType=wxEVT_MESSAGE_BOX)
        self.message = message
        self.caption = caption
        self.style = style
        self.commandQueue = commandQueue
        self.returnObject = returnObject
