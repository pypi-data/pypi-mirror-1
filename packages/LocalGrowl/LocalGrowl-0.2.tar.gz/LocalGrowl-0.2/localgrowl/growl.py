"""Implementation to use Growl.

Typical usage:
g = Growl("Hi", "Hello from Safari", a="Safari")
g.notify()
"""

import os

class Growl():
    """Implements interface to Growl"""
    
    def __init__(self, title, message, **options):
        """Notifications must always have a title and message.
        
        For other features like specifiying the app icon and such use the 
        argument of growlnotify, ie: a or appIcon.
        
        And for options that are yes or no answers use 0 for no and 1 for yes.
        """
        self.title = title
        self.message = message
        self.options = options
        self.command = 'growlnotify -t "%s" -m "%s"' \
        % (self.title, self.message)
        return None
        
    def notify(self):
        """Calls method to create the options for growlnotify
        and then runs command.
        """
        self.create_command()
        os.system(self.command)
        return None
        
    def create_command(self):
        """Creates options for growlnotify command."""
        for key, value in self.options.items():
            if key != 0 and len(key) > 1:
                self.command += " --%s %s" % (key, value)
            elif key != 0 and len(key) == 1:
                self.command += " -%s %s" % (key, value)
        return self.command

