from itertools import count

idCounter = count()

JU_XMPP_INITIALIZE=idCounter.next()
JU_XMPP_CONNECT=idCounter.next()
JU_XMPP_CANCEL_CONNECT=idCounter.next()
JU_XMPP_DISCONNECT=idCounter.next()
JU_XMPP_SET_PRESENCE=idCounter.next()
JU_XMPP_SEND_IQ_STANZA=idCounter.next()
JU_XMPP_SEND_IQ_STANZA_REPLY=idCounter.next()
JU_XMPP_REC_IQ_STANZA=idCounter.next()
JU_USER_ANSWER=idCounter.next()
JU_LOCAL_TURN_ACTION=idCounter.next()
JU_XMPP_OPEN_MUC=idCounter.next()

class JuCommand:
    """Parent class for all Jubatu-specific commands.
    
    All this commands are independent from the wx command hierarchy.
    """
    
    def __init__(self, id):
        self.id = id
        
class JuXmppInitializeCommand(JuCommand):
    """Ask the setting of new xmpp data (user, password, server, ...)"""
    
    def __init__(self, jid, password, server):
        self.jid = jid
        self.password = password
        self.server = server
        JuCommand.__init__(self, JU_XMPP_INITIALIZE)

class JuXmppConnectCommand(JuCommand):
    """Ask the stablishment of a xmpp connection"""
    
    def __init__(self):
        JuCommand.__init__(self, JU_XMPP_CONNECT)

class JuXmppCancelConnectCommand(JuCommand):
    """Ask the cancelation of an ongoing xmpp connection"""
    
    def __init__(self):
        JuCommand.__init__(self, JU_XMPP_CANCEL_CONNECT)

class JuXmppDisconnectCommand(JuCommand):
    """Ask the disconnection of the current xmpp session."""
    
    def __init__(self):
        JuCommand.__init__(self, JU_XMPP_DISCONNECT)

class JuXmppSetPresence(JuCommand):
    """Ask the user's xmpp presente to be set to a given status."""
    
    def __init__(self, show=None):
        self.show = show
        JuCommand.__init__(self, JU_XMPP_SET_PRESENCE)

class JuXmppSendIqStanza(JuCommand):
    """Ask the sending of a provided iq stanza.
    
    This will be commonly used by the game modules to send the game-relative info to the other players,
    as the protocols are implemented by using xmpp iq stanzas.
    """
    
    #def __init__(self, toJid, type, payload, res_handler, err_handler, timeout_handler=None, timeout=300, iq_id=None):
    def __init__(self, stanza, res_handler, err_handler, timeout_handler=None, timeout=300):
        #self.to_jid = toJid
        #self.type = type
        #self.payload = payload
        #self.iq_id = iq_id
        self.stanza = stanza
        self.res_handler = res_handler
        self.err_handler = err_handler
        self.timeout_handler = timeout_handler
        self.timeout = timeout
        JuCommand.__init__(self, JU_XMPP_SEND_IQ_STANZA)

class JuXmppSendIqStanzaReply(JuCommand):
    """Ask the sending of a stanza reply for a previously received iq stanza."""
    
    def __init__(self, stanza):
        self.stanza = stanza
        JuCommand.__init__(self, JU_XMPP_SEND_IQ_STANZA_REPLY)

class JuXmppRecIqStanza(JuCommand):
    """Ask the processing of a received iq stanza.
    
    Typically, the communication thread will send this commands to the game modules for them to
    take appropiate actions.
    """
    
    def __init__(self, stanza, handler=None):
        self.stanza = stanza
        self.handler = handler
        JuCommand.__init__(self, JU_XMPP_REC_IQ_STANZA)

class JuUserAnswer(JuCommand):
    """Ask the processing of a user provided answer.
    
    The attached info will store information about the user answer. This should be used for non
    protocol-dependent answers (as the user's answer to a question shown in a message box).
    """
    
    def __init__(self, answer, attachedObject):
        self.answer = answer
        self.attachedObject = attachedObject
        JuCommand.__init__(self, JU_USER_ANSWER)
        
class JuLocalTurnAction(JuCommand):
    """Ask the processing of the actions corresponding to a certain turn of the game.
    
    Normally, this will be used for intra-communication between the game GUIs and their respective engines.
    The info provided by the GUI should be enough for the engine to send the correponding iq stanzas to
    the other players (according to the game specific protocol) or/and to take whatever other game-dependent actions.
    How the info is passed is expected to be highly game-dependent.
    """
    
    def __init__(self, action):
        self.action = action
        JuCommand.__init__(self, JU_LOCAL_TURN_ACTION)
        
class JuXmppOpenMuc(JuCommand):
    """Ask the opening of a Muc. NOT IMPLEMENTED BY NOW."""
    
    def __init__(self):
        JuCommand.__init__(self, JU_XMPP_OPEN_MUC)
