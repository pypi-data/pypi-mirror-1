import Queue
#import threading

#class BaseEngine(threading.Thread):
class BaseEngine:
    """Base class for all the game engines.
    
    Don't do nothing but to provide some default messages and to provide access to common resources.
    Could be extended in the future to manage some other tasks usually common to all games, discharging
    the modules from that work.
    """
    
    commandsQueue = Queue.Queue()

    def __init__(self):
        #threading.Thread.__init__(self)
        pass

    def name(self):
        return "Unnamed game"
    def description(self):
        return "No description available"
    def run(self):
        pass
    def run_step(self):
        pass
