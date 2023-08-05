import os
import wx
import events
import logging
import md5


def file_hash(file):
    """Return a hash of the content of a file (encoded as a hex string)."""
    
    hash = md5.new()
    fb = open(file, 'rb')
    readBytes = 4192;
    while (readBytes):
        readString = fb.read(readBytes);
        hash.update(readString);
        readBytes = len(readString);
    fb.close()
    
    return hash.hexdigest()

def get_preferred_languages():
    """Return the preferred languages according with user's settings."""
    
    userLang = wx.GetApp().userData.get('configuration', 'language').split(',')
    
    if (len(userLang) == 0):
        return ['es']
    else:
        return userLang
    
def get_user_data_path():
    "Convenience function to get the full path for the user specific data file."
    
    return os.path.join(get_user_dir(), 'userdata')

def get_user_dir():
    """Return the directory used to store the user specific data. (Selected language, etc.)"""
    
    configPath = os.path.join(os.path.expanduser("~"), ".jubatu")
    logging.getLogger("core").debug("User data dir: %s", configPath)
    return configPath

def get_game_dirs():
    """Return a list with the root directories for game modules.
    
    A couple of directories can hold the game modules: the directorie where the main jubatu module
    is located, and a user-dependent one (located in whatever place the OS use to locate user's profiles).
    """
    
    dirList = []
    path = os.path.join(os.getcwdu(), "games")
    logging.getLogger("core").debug("Path #1: %s", path)
    if os.path.exists(path):
        dirList.append(path)
    path = os.path.join(get_user_dir(), "games")
    logging.getLogger("core").debug("Path #2: %s", path)
    if os.path.exists(path):
        dirList.append(path)
    return dirList

def random_hex_string(numberOfBytes):
    """Return a random number formatted as a hex string.
    
    numberOfBytes -- number of random bytes asked (every byte will be formatted as a couple of hex digits)
    
    The implementation rely on os.urandom, which *should* be a reliable and criptografically secure
    random number generator. This will depend heavily on the OS, however.
    """
    
    aux = os.urandom(numberOfBytes)
    randomString = ""
    
    for i in range(numberOfBytes):
        randomString += hex(ord(aux[i]))[2:]
        
    return unicode(randomString)
    
    
class BuddySelectionManager:
    """Helper class to simplify the selection of buddies for games' player lists.
    
    At least one object of this class will be stored in the root Jubatu class to manages the selection of buddies
    when filling players lists. Once a game module have given the focus to the corresponding list, all
    JuBuddySelection events will be processed by this manager and redirected to the given handlers.
    """
    
    last_control = None
    
    def buddy_selection_received(self, event):
        """Handler to manage the suscription of the manager to whoever be publising the JuBuddySelection events.
        
        This function should be binded to the JuBuddySelection's publisher by whoever be creating a new manager.
        """
        
        if (self.last_control is not None) and (event.control is None):
            logging.getLogger("core").debug("Last control: %s", self.last_control)
            event.control = self.last_control
            self.last_control.AddPendingEvent(event)

    def buddy_input_list_focused(self, event):
        """Callback to the focusing of a managed control
        
        event -- The pyEvent object containing the info about the focusing
        
        This function will execute when a control managed by this object have just received the focus.
        That mean that the manager will be passing him all the JuBuddySelection events until another
        control got the focus.
        """
        
        self.last_control=event.GetEventObject()
        logging.getLogger("core").debug("The control %s is now the receiver of 'buddy selected' signals.", self.last_control.GetClassName())

    def buddy_selection_bind(self, control, handler):
        """Bind a certain control with a game module-dependent handler to manage the selection of a buddy.
        
        control -- The control that will receive the new player; usually, a listbox.
        handler -- The handler that will manage the receipt of a new player for that list.
        
        This function must be called by the game modules to bind the player lists with their correponding
        handler to manage a buddy selection for that list.
        """
        
        logging.getLogger("core").debug("Control: %s, Handler: %s", control, handler)
        control.Bind(events.EVT_BUDDY_SELECTED, handler)
        control.Bind(wx.EVT_SET_FOCUS, self.buddy_input_list_focused)
