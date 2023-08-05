from dist_plone import Software, PyModule, ZProduct, Bundle

BASE = 'http://osdn.dl.sourceforge.net/sourceforge/'

PLONE_BASE = BASE + 'plone/'
PLONE_BASE = 'http://antiloop.plone.org/download/'
PLONE_GOOGLE = "http://plone.googlecode.com/files/"

PLONE_DIST = 'http://dist.plone.org/'
PLONE_ORG = 'http://plone.org/products/'
OSCOM_ORG = 'http://kupu.oscom.org/'
ZOPE_ORG = 'http://www.zope.org/Products/'

CHEESE_SOURCE = 'http://pypi.python.org/packages/source/'

PLONE_CORE = [
    Bundle('CMF',
           ZOPE_ORG + 'CMF/CMF-2.1.0/CMF-2.1.0.tar.gz',
           { 'CMFActionIcons': ZProduct,
             'CMFCalendar': ZProduct,
             'CMFCore'    : ZProduct,
             'CMFDefault' : ZProduct,
             'CMFTopic'   : ZProduct,
             'CMFUid'     : ZProduct,
             'DCWorkflow' : ZProduct,
           }
    ),
    ZProduct('GenericSetup', ZOPE_ORG + 'GenericSetup/GenericSetup-1.3.2/GenericSetup-1.3.2.tar.gz'),
    ZProduct('ATContentTypes', PLONE_ORG + 'atcontenttypes/releases/1.2.2/ATContentTypes-1.2.2.tgz'),
    ZProduct('ATReferenceBrowserWidget', PLONE_ORG + 'atreferencebrowserwidget/releases/2.0.1/ATReferenceBrowserWidget-2.0.1.tar.gz'),
    ZProduct('CMFDynamicViewFTI', PLONE_ORG + 'cmfdynamicviewfti/releases/3.0.1/CMFDynamicViewFTI-3.0.1.tar.gz'),
    ZProduct('CMFFormController', PLONE_ORG + 'cmfformcontroller/releases/2.1.1/CMFFormController-2.1.1.tar.gz'),
    ZProduct('CMFPlacefulWorkflow', PLONE_ORG + 'cmfplacefulworkflow/releases/1.2.1/cmfplacefulworkflow-1-2-1.tgz'),
    ZProduct('CMFPlone', PLONE_DIST + 'PloneBase-3.0.3.tar.gz'),
    ZProduct('CMFQuickInstallerTool', PLONE_ORG + 'cmfquickinstallertool/releases/2.0.3/CMFQuickInstallerTool-2.0.3.tar.gz'),
    ZProduct('CMFDiffTool', PLONE_ORG + 'cmfdifftool/releases/0.3.4/cmfdifftool-0-3-4.tgz'),
    ZProduct('CMFTestCase', PLONE_ORG + 'cmftestcase/releases/0.9.6/CMFTestCase-0.9.6.tar.gz'),
    ZProduct('ExtendedPathIndex', PLONE_ORG + 'extendedpathindex/releases/2.4/ExtendedPathIndex-2.4.tgz'),
    ZProduct('ExternalEditor', PLONE_ORG + 'external-editor/releases/0.9.3/ExternalEditor-0.9.3-src.tgz'),
    ZProduct('GroupUserFolder', PLONE_ORG + 'groupuserfolder/releases/3.55.1/groupuserfolder-3-55-1.tgz'),
    ZProduct('kupu', PLONE_ORG + 'kupu/releases/1.4.4/kupu-1-4-4.tgz'),
    ZProduct('PlacelessTranslationService',  PLONE_ORG + 'pts/releases/1.4.5/PlacelessTranslationService-1.4.5.tar.gz'),
    ZProduct('PloneTestCase',PLONE_ORG + 'plonetestcase/releases/0.9.6/PloneTestCase-0.9.6.tar.gz'),
    ZProduct('PloneTranslations', PLONE_ORG + 'plonetranslations/releases/3.0.7/PloneTranslations-3.0.7.tar.gz'),
    ZProduct('PloneLanguageTool', PLONE_ORG + 'plonelanguagetool/releases/2.0.1/PloneLanguageTool-2.0.1.tar.gz'),
    ZProduct('SecureMailHost', PLONE_ORG + 'securemailhost/releases/1.1/SecureMailHost-1.1.tar.gz'),
    ZProduct('ResourceRegistries', PLONE_ORG + 'resourceregistries/releases/1.4.1/resourceregistries-1-4-1.tgz'),
    ZProduct('statusmessages', PLONE_ORG + 'statusmessages/releases/3.0.2/statusmessages-3.0.2.tar.gz'),
    ZProduct('PlonePAS', PLONE_ORG + 'plonepas/releases/3.1/PlonePAS-3.1.tar.gz'),
    ZProduct('PluggableAuthService', ZOPE_ORG + 'PluggableAuthService/PluggableAuthService-1.5.1/PluggableAuthService-1.5.1.tar.gz', 'PluggableAuthService-1.5.1'),
    ZProduct('PasswordResetTool', PLONE_ORG + 'passwordresettool/releases/1.0/PasswordResetTool-1.0.tar.gz'),
    ZProduct('PluginRegistry', ZOPE_ORG + 'PluginRegistry/PluginRegistry-1.1.2/PluginRegistry-1.1.2.tar.gz', 'PluginRegistry-1.1.2'),
    ZProduct('ZopeVersionControl', 'http://antiloop.plone.org/download/ZopeVersionControl-0.3.4.tar.gz'),
    ZProduct('CMFEditions', PLONE_ORG + 'cmfeditions/releases/1.1.2/CMFEditions-1.1.2.tgz'),
    ZProduct('NuPlone', PLONE_ORG + 'nuplone/releases/0.9.3/NuPlone-0.9.3.tgz'),
    ZProduct('AdvancedQuery', 'http://www.dieter.handshake.de/pyprojects/zope/AdvancedQuery.tgz'),
]

PLONE_CORE_PACKAGES = [
    PyModule('archetypes.kss', CHEESE_SOURCE + 'a/archetypes.kss/archetypes.kss-1.2.3.tar.gz', version="1.2.3"),
    PyModule('kss.core', CHEESE_SOURCE + 'k/kss.core/kss.core-1.2.3.tar.gz', version="1.2.3"),
    PyModule('plone.app.content', CHEESE_SOURCE + 'p/plone.app.content/plone.app.content-1.0.1.tar.gz', version="1.0.1"),
    PyModule('plone.app.contentmenu', CHEESE_SOURCE + 'p/plone.app.contentmenu/plone.app.contentmenu-1.0.3.tar.gz', version="1.0.3"),
    PyModule('plone.app.contentrules', CHEESE_SOURCE + 'p/plone.app.contentrules/plone.app.contentrules-1.0.2.tar.gz', version="1.0.2"),
    PyModule('plone.app.controlpanel', CHEESE_SOURCE + 'p/plone.app.controlpanel/plone.app.controlpanel-1.0.2.tar.gz', version="1.0.2"),
    PyModule('plone.app.customerize', CHEESE_SOURCE + 'p/plone.app.customerize/plone.app.customerize-1.0.tar.gz', version="1.0"),
    PyModule('plone.app.form', CHEESE_SOURCE + 'p/plone.app.form/plone.app.form-1.0.3.tar.gz', version="1.0.3"),
    PyModule('plone.app.i18n', CHEESE_SOURCE + 'p/plone.app.i18n/plone.app.i18n-1.0.tar.gz', version="1.0"),
    PyModule('plone.app.iterate', CHEESE_SOURCE + 'p/plone.app.iterate/plone.app.iterate-1.0.tar.gz', version="1.0"),
    PyModule('plone.app.kss', CHEESE_SOURCE + 'p/plone.app.kss/plone.app.kss-1.2.3.tar.gz', version="1.2.3"),
    PyModule('plone.app.layout', CHEESE_SOURCE + 'p/plone.app.layout/plone.app.layout-1.0.3.tar.gz', version="1.0.3"),
    PyModule('plone.app.linkintegrity', CHEESE_SOURCE + 'p/plone.app.linkintegrity/plone.app.linkintegrity-1.0.2.tar.gz', version="1.0.2"),
    PyModule('plone.app.openid', CHEESE_SOURCE + 'p/plone.app.openid/plone.app.openid-1.0.1.tar.gz', version="1.0.1"),
    PyModule('plone.app.portlets', CHEESE_SOURCE + 'p/plone.app.portlets/plone.app.portlets-1.0.3.tar.gz', version="1.0.3"),
    PyModule('plone.app.redirector', CHEESE_SOURCE + 'p/plone.app.redirector/plone.app.redirector-1.0.2.tar.gz', version="1.0.2"),
    PyModule('plone.app.viewletmanager', CHEESE_SOURCE + 'p/plone.app.viewletmanager/plone.app.viewletmanager-1.0.tar.gz', version="1.0"),
    PyModule('plone.app.vocabularies', CHEESE_SOURCE + 'p/plone.app.vocabularies/plone.app.vocabularies-1.0.1.tar.gz', version="1.0.1"),
    PyModule('plone.app.workflow', CHEESE_SOURCE + 'p/plone.app.workflow/plone.app.workflow-1.0.1.1.tar.gz', version="1.0.1.1"),
    PyModule('plone.contentrules', CHEESE_SOURCE + 'p/plone.contentrules/plone.contentrules-1.0.1.1.tar.gz', version="1.0.1.1"),
    PyModule('plone.fieldsets', CHEESE_SOURCE + 'p/plone.fieldsets/plone.fieldsets-1.0.tar.gz', version="1.0"),
    PyModule('plone.i18n', CHEESE_SOURCE + 'p/plone.i18n/plone.i18n-1.0.1.tar.gz', version="1.0.1"),
    PyModule('plone.intelligenttext', CHEESE_SOURCE + 'p/plone.intelligenttext/plone.intelligenttext-1.0.tar.gz', version="1.0"),
    PyModule('plone.locking', CHEESE_SOURCE + 'p/plone.locking/plone.locking-1.0.tar.gz', version="1.0"),
    PyModule('plone.memoize', CHEESE_SOURCE + 'p/plone.memoize/plone.memoize-1.0.3.tar.gz', version="1.0.3"),
    PyModule('plone.openid', CHEESE_SOURCE + 'p/plone.openid/plone.openid-1.0.1.tar.gz', version="1.0.1"),
    PyModule('plone.portlets', CHEESE_SOURCE + 'p/plone.portlets/plone.portlets-1.0.3.tar.gz', version="1.0.3"),
    PyModule('plone.session', CHEESE_SOURCE + 'p/plone.session/plone.session-1.1.tar.gz', version="1.1"),
    PyModule('plone.theme', CHEESE_SOURCE + 'p/plone.theme/plone.theme-1.0.tar.gz', version="1.0"),
    PyModule('wicked', CHEESE_SOURCE + 'w/wicked/wicked-1.1.6.tar.gz', version="1.1.6"),
    PyModule('five.customerize', CHEESE_SOURCE + 'f/five.customerize/five.customerize-0.2.tar.gz', version="0.2"),
    PyModule('five.localsitemanager', CHEESE_SOURCE + 'f/five.localsitemanager/five.localsitemanager-0.2.tar.gz', version="0.2"),
]


ADDONS = [
]

AT1_5 = [
    ZProduct('Archetypes', PLONE_ORG + 'archetypes/releases/1.5/Archetypes-1.5.4.tgz'),
]

README_TXT = """Plone's README is in CMFPlone/README.txt
"""

class Distribution:

    target = 'independent'

    # this is what plone is based on
    python =  Software('python', 'http://www.python.org/ftp/python/2.4.4/Python-2.4.4.tgz')
    zope   =  Software('zope'  , ZOPE_ORG + 'Zope/2.10.5/Zope-2.10.5-final.tgz')

    # plone core
    core   = PLONE_CORE + AT1_5
    # plone core packages
    core_packages = PLONE_CORE_PACKAGES

    # plone addons
    addons = ADDONS

    # the readme.txt
    readme = README_TXT

    # documentation to copy to the tar root
    documentation = [ 'README.txt', 'INSTALL.txt', 'RELEASENOTES.txt' ]

