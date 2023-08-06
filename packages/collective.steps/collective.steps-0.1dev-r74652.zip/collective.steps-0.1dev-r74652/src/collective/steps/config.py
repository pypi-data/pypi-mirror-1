#config file for Stepper

from collective.steps import common

prepare = common.prepare

# COMMON CHAINS
chains = {}

# AGAPE CHAINS
agape_chains = {'agape_mode_dev': ['profile_agape_default', 'profile_agape_dev', 'init_users_password', 'init_users_email'],
                'agape_mode_preprod': ['profile_agape_default', 'profile_agape_preprod', 'init_users_password', 'init_users_email'],
                'agape_mode_prod': ['profile_agape_default', 'profile_agape_prod']}
chains.update(agape_chains)


steps = {'profile_default':('collective.steps.profile.Profile',
                           ('profile-Products.CMFPlone:plone',)),
                           
         'init_users_password':('collective.steps.members.Password',
                               ('secret',)),
                           
         'init_users_email':('collective.steps.members.EMail',
                            ('sylvain.boureliou@makina-corpus.com',)),
           
         # AGAPE STEPS
         
         'profile_agape_default':('collective.steps.profile.Profile',
                                  ('profile-agape.policy:agape',)),
                                  
         'profile_agape_dev':('collective.steps.profile.Profile',
                              ('profile-agape.policy:agapedev',)),
                              
         'profile_agape_preprod':('collective.steps.profile.Profile',
                                  ('profile-agape.policy:agapepreprod',)),
                                  
         'profile_agape_prod':('collective.steps.profile.Profile',
                               ('profile-agape.policy:agapeprod',)),
}
