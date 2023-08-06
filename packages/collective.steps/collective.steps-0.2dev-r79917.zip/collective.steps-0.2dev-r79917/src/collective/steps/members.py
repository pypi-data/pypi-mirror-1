# -*- coding: utf-8 -*-

from DateTime.DateTime import DateTime
from Products.Stepper.step import Step

import logging
logger = logging.getLogger('collective.steps.members')

class Member(Step):
    """Base step that returns all the members from portal_membership"""
    def getSequence(self):
        pm = self.root.portal_membership
        return pm.listMembers()

class Password(Member):
    """Change password of all members in your plone site.
    Usefull if you use a copy of a production database, and a user report you
    a problem.

    args:
    - password: the password to set to all members
    """
    commit_sequence = True

    def __init__(self, root, *args):
        Member.__init__(self, root, *args)
        self.password = args[0] #may i need to validate that is a mail ?
        self.doChangeUser = self.root.acl_users.source_users.doChangeUser

    def process(self, member):
        self.doChangeUser(member.getId(), self.password)


class EMail(Member):
    """Change email of all members in your plone site.
    That can be convinient when you work on a copy of the production
    database and if you are afraid to send mail.

    args:
    - email: the email to set to all members
    """
    commit_sequence = True
    def __init__(self, root, *args):
        Member.__init__(self, root, *args)
        self.email = args[0] #may i need to validate that is a mail ?

    def process(self, member):
        member.setMemberProperties({"email": self.email})

class PASPlugins(Step):
    """Manage PAS plugins, you can activate/unactivate plugins
    args:
    - interface name: the name of the interface you want to change status
    - status: must be in "activate"/"deactivate"
    """
    def __init__(self, root, *args):
        Step.__init__(self, root, *args)
        self.ifaces = {}
        for p in self.root.acl_users.plugins._plugin_types:
            self.ifaces[p.__name__] = p
        self.pluginregistry = self.root.acl_users.plugins
        self.iface_name = self.arg[0]

    def getSequence(self):
        return self.root.acl_users.plugins.getAllPlugins(self.args[0])

    def process(self, plugin):
        if self.args[1] == 'deactivate':
            self.pluginregistry.deactivatePlugin(self.ifaces[self.iface_name],
                                                 plugin)
        elif self.args[1] == 'activate':
            self.pluginregistry.activatePlugin(self.ifaces[self.iface_name], plugin)

class AddMember(Step):
    """Add a member
    args:
       username: for example 'webmestre'
       password: for example 'secret'
       roles: user's roles, for example ['Member', 'Manager']
    """
    commit_sequence = True

    def process(self, args):
        username, password, roles = self.args
        mtool = self.root.portal_membership
        member = mtool.getMemberById(username)
        mtool.addMember(username, password, roles, [])
        #addMember doesn't raise exception if user already exists.

class ClearExpiredAccount(Step):
    """This step take all members accounts not activated and register
    in password reset tool to delete them

    Note that by default password_reset_tool when a new password request is
    started, delete all expired request that has more than ten days. I advise
    you to add the monkey patch bellow, somewhere and to add this step in a cron

    from Products.PasswordResetTool.PasswordResetTool import PasswordResetTool
    def clearExpired(self, days=10): pass
    PasswordResetTool.clearExpired = clearExpired
    logger.info('password reset tool is now patched, clearExpired do nothing')

    I don't this it is a good idea to integrate this step in the clearExpired
    method of the PasswordResetTool because the cost is

    """

    commit_object = False

    commit_sequence = True

    def getSequence(self):
        """Return all the member not alreaduy logged and mark as expire to
        change their password
        """
        expired_ids = []
        pass_reset = getToolByName(self.root, 'portal_password_reset')
        pm = getToolByName(self.root, 'portal_membership')
        items = pass_reset._requests.items()
        return items

    def process(self, item):
        """Remove them from password reset tool and delete their accounts"""
        key, record = item
        user_id, expiry = record
        pm = self.root.portal_membership
        pass_reset = self.root.portal_password_reset
        days = pass_reset._timedelta / 24
        if pass_reset.expired(expiry, DateTime()-days):
            del pass_reset._requests[key]
            pass_reset._p_changed = 1 #password resettool use simple dict
            logger.info("remove %s from expired in password reset tool"%user_id)
            if user_id in pm.listMemberIds():
                logger.info("he is in member ids")
                user = pm.getMemberById(user_id)
                pp = user.getProperty(self.args[0])
                logger.info("%s %s"%(pp, self.args[1]))
                account_unactivated = pp == self.args[1]
                if account_unactivated:
                    pm.deleteMembers([user_id],
                             delete_memberareas=1,
                             delete_localroles=0) # =1 => This can take days

