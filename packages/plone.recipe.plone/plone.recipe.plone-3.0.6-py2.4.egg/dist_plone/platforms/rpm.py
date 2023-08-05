from dist_plone import Software, PyModule, ZProduct, Bundle
from independent import Distribution as Base

# NOTE: this file holds a platform/packaging specific plone 
#       distribution definition. To use a specific distribution
#       instead of the general platform/package independent
#       one add --target={DISTRIBUTION} as parameter


# defines local addons which are required
PLONE_CORE = []

# defines optional addons
ADDONS = []


class Distribution(Base):

    target = 'rpm'

    # this is what plone is based on
    python =  Base.python
    zope   =  Base.zope

    # plone core
    core   = Base.core + PLONE_CORE

    # plone addons
    addons = Base.addons + ADDONS

