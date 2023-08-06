# -*- coding: utf-8 -*-

from Products.Stepper.step import Step

import logging
logger = logging.getLogger('AntiCancerMigration.profile')

class Profile(Step):
    """Apply a profile
    args:
    - profile name: 'profile-Products.CMFPlone:plone' for example
    """
    commit_sequence = True

    def process(self, profile):
        plone = self.root
        setup_tool = plone.portal_setup
        setup_tool.runAllImportStepsFromProfile(profile)
