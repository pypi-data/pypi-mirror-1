"""Implementation to use Growl."""

import os

class Growl():
    """Implements interface to Growl"""
    def __init__(self, title, message, **options):
        """Notifications must always have a title and message.
        
        For other features like specifiying the app icon and such use the 
        argument of growlnotify, ie: a for appicon.
        """
        self.title = title
        self.message = message
        self.options = options
        self.command = 'growlnotify -t "%s" -m "%s"' % (self.title, self.message)
        
    def notify(self):
        self.create_command()
        os.system(self.command)
        return None
        
    def create_command(self):
        for key, value in self.options.items():
            if key != 0:
                self.command += " -%s %s" % (key, value)
        return self.command
