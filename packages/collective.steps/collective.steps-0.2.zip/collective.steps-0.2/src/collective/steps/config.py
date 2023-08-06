# -*- coding: utf-8 -*-

#config file for Stepper

from collective.steps import common

prepare = common.prepare

chains = {}

steps = {'profile_default':('collective.steps.profile.Profile', ('profile-Products.CMFPlone:plone',)),
         'init_users_password':('collective.steps.members.Password', ('secret',)),
         'del_unactivated_account':('Products.ClearExpiredAccount.step.ClearExpiredAccount',
                       ("last_login_time",DateTime("2000/01/01"))),
         'email':('collective.steps.members.EMail', ('mail@provider.com',))
}
