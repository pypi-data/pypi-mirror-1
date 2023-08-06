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

