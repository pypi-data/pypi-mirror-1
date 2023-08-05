from p4a.common import site
from lovely.tag import interfaces
from p4a.plonetagging import content
from p4a.plonetagging import interfaces as ptifaces
import five.intid.site
from Products.CMFCore import utils as cmfutils

import logging
logger = logging.getLogger('p4a.plonetagging.sitesetup')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False

def setup_z3site(portal):
    site.ensure_site(portal)

    sm = portal.getSiteManager()
    if not sm.queryUtility(interfaces.ITaggingEngine):
        # registerUtility api changed between Zope 2.9 and 2.10
        if HAS_FLSM:
            sm.registerUtility(content.ContentTaggingEngine(),
                               interfaces.ITaggingEngine)
        else:
            sm.registerUtility(interfaces.ITaggingEngine,
                               content.ContentTaggingEngine())

    if not sm.queryUtility(ptifaces.ITaggingConfig):
        # registerUtility api changed between Zope 2.9 and 2.10
        if HAS_FLSM:
            sm.registerUtility(content.TaggingConfig(),
                               ptifaces.ITaggingConfig)
        else:
            sm.registerUtility(ptifaces.ITaggingConfig,
                               content.TaggingConfig())

    installer = five.intid.site.FiveIntIdsInstall(portal, {})
    if not installer.installed:
        installer.install()

def setup_deps(portal):
    quickinstaller = portal.portal_quickinstaller
    for dep in ('CMFonFive',):
        quickinstaller.installProduct(dep)

def setup_indexes(portal):
    """Install specific indexes for the audio metadata fields
    so they are searchable.

    """

    catalog = cmfutils.getToolByName(portal, 'portal_catalog')

    reindex = False
    if not 'tags' in catalog.schema():
        catalog.manage_addColumn('tags')
        reindex = True

    if not 'tags' in catalog.indexes():
        catalog.addIndex('tags', 'KeywordIndex')
        reindex = True

    if reindex:
        catalog.manage_reindexIndex('tags')

INDEX_MAPPING = {'tags':
                    {'name': 'Tags',
                     'description': 'The tags.',
                     'enabled': True,
                     'criteria': ('ATSimpleStringCriterion',
                                  'ATListCriterion',)},
                 }

def setup_configlet(portal):
    """Setup the plone configlet."""

    portal_conf = cmfutils.getToolByName(portal, 'portal_controlpanel')
    portal_conf.unregisterConfiglet('p4a.plonetagging')
    portal_conf.registerConfiglet(
        'p4a.plonetagging',
        'Content Tagging',
        'string:${portal_url}/tagging-config.html',
        '',                 # a condition
        'Manage portal',    # access permission
        'Products',         # section to which the configlet should be added:
                            #(Plone,Products,Members)
        1,                  # visibility
        'p4a.plonetagging',
        'site_icon.gif', # icon in control_panel
        'Configure tagging settings.',
        None)

def setup_smart_folder_indexes(portal):
    """Adds the default indexes to be available from smartfolders"""
    atct_config = cmfutils.getToolByName(portal, 'portal_atct')

    for index, index_info in INDEX_MAPPING.items():
        atct_config.updateIndex(index, friendlyName=index_info['name'],
                                description=index_info['description'],
                                enabled=index_info['enabled'],
                                criteria=index_info['criteria'])
        atct_config.updateMetadata(index, friendlyName=index_info['name'],
                                   description=index_info['description'],
                                   enabled=True)

def setup_portal(portal):
    setup_indexes(portal)
    setup_smart_folder_indexes(portal)
    setup_deps(portal)
    setup_configlet(portal)
    setup_z3site(portal)
