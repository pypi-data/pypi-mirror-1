from Products.CMFCore.utils import getToolByName
from plone.app.workflow.remap import remap_workflow

import logging
logger = logging.getLogger('PloneGazette.migration')


def migrateTo311(context):
    portal = context.portal_url.getPortalObject()
    type_ids = ('Subscriber',)
    chain = ('subscriber_workflow',)
    state_map = {'published': 'published'}
    logger.info('Remapping Subscriber workflow')
    remap_workflow(context, type_ids=type_ids, chain=chain,
                   state_map=state_map)
    logger.info('Subscriber workflow remapped')
