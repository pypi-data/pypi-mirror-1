from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from Products.CMFCore.DirectoryView import registerDirectory

from betahaus.debug import config


import logging
logger = logging.getLogger(config.PROJECTNAME)



def initialize(context):
    """ nothing needed"""
    pass 
        