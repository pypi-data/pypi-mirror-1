try:
    from Products.GenericSetup import EXTENSION
    from Products.GenericSetup import profile_registry
    
    from Products.CMFPlone.interfaces import IPloneSiteRoot
except ImportError:
    # Tolerate missing import for running tests
    pass

def initialize(context):
    profile_registry.registerProfile(
        'writeheavy',
        'collective.coreloadtests writeheavy',
        'Extension profile for collective.coreloadtests writeheavy.',
        'profiles/writeheavy',
        'collective.coreloadtests',
        EXTENSION,
        for_=IPloneSiteRoot)
    profile_registry.registerProfile(
        'contentcreation',
        'collective.coreloadtests contentcreation',
        'Extension profile for collective.coreloadtests contentcreation.',
        'profiles/contentcreation',
        'collective.coreloadtests',
        EXTENSION,
        for_=IPloneSiteRoot)
