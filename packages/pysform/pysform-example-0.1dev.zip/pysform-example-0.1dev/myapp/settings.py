from os import path
from werkzeug.routing import Rule
from pysmvt.config import DefaultSettings
import pysapp.settings

basedir = path.dirname(path.abspath(__file__))
appname = path.basename(basedir)

class Default(pysapp.settings.Default):
    """ Default settings should be good for production.  User-specific
    development environments can be created below.  """
    
    def __init__(self):
        # call parent init to setup default settings
        pysapp.settings.Default.__init__(self, appname, basedir)
        
        # can be used for display purposes through the app
        self.name.full = 'myapp'
        self.name.short = 'myapp'
        
        # supporting applications
        self.supporting_apps = ['pysapp']
        
        # application modules from our application or supporting applications
        self.modules.default.enabled = True
        
        #######################################################################
        # ROUTING
        #######################################################################
        self.routing.routes.extend([
            Rule('/', defaults={}, endpoint='default:Index')
        ])
        
        #######################################################################
        # DATABASE
        #######################################################################
        self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'application.db')
        
        #######################################################################
        # EMAIL ADDRESSES
        #######################################################################
        # the default 'from' address used if no from address is specified
        self.emails.from_default = 'randy@rcs-comp.com'
        
        # programmers who would get system level notifications (code
        # broke, exception notifications, etc.)
        self.emails.programmers = ['randy@rcs-comp.com']
        
        # people who would get application level notifications (payment recieved,
        # action needed, etc.)
        self.emails.admins = ['randy@rcs-comp.com']
        
        #######################################################################
        # EMAIL SETTINGS
        #######################################################################
        # used by mail_admins() and mail_programmers()
        self.email.subject_prefix = '[%s] ' % appname
        
        #######################################################################
        # EXCEPTION HANDLING
        #######################################################################
        self.exceptions.hide = True
        self.exceptions.email = True
        
        #######################################################################
        # DEBUGGING
        #######################################################################
        self.debugger.enabled = False

class Dev(Default):
    """ this custom "user" class is designed to be used for
    user specific development environments.  It can be used like:
    
        `pysmvt serve dev`
    """
    def __init__(self):
        Default.__init__(self)
                
        # a single or list of emails that will be used to override every email sent
        # by the system.  Useful for debugging.  Original recipient information
        # will be added to the body of the email
        self.emails.override = 'you@example.com'
        
        #######################################################################
        # USERS: DEFAULT ADMIN
        #######################################################################
        self.modules.users.admin.username = 'you'
        self.modules.users.admin.password = 'kkkpbd'
        self.modules.users.admin.email = 'you@example.com'
        
        #######################################################################
        # EXCEPTION HANDLING
        #######################################################################
        self.exceptions.hide = False
        self.exceptions.email = False
        
        #######################################################################
        # DEBUGGING
        #######################################################################
        self.debugger.enabled = True
        # this is a security risk on a live system, so we only turn it on
        # for a specific user config
        self.debugger.interactive = True
# this is just a convenience so we don't have to type the capital letter on the
# command line when running `pysmvt serve`
dev=Dev


