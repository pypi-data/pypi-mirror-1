from Products.CMFCore.utils import getToolByName


def add_catalog_indexes(site, logger):
    """Add our indexes to the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.
    """
    catalog = getToolByName(site, 'portal_catalog')
    indexes = catalog.indexes()
    wanted = (("main_date", "DateIndex"),
             )
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def setup(context):
    # Only run step if a flag file is present
    if context.readDataFile('plonehrm.absence.txt') is None:
        return
    logger = context.getLogger('plonehrm.absence')
    site = context.getSite()
    add_catalog_indexes(site, logger)
    logger.info('plonehrm.absence_various step imported')
