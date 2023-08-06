#
# $Id: __init__.py 58836 2008-02-17 14:22:30Z naro $
#

"""Newsletter Plone"""

__version__ = "$Revision: 58836 $" [11:-2]

## Archetypes import
from Products.Archetypes.public import *
from Products.Archetypes import listTypes

## CMF imports

from Products.CMFCore.utils import ContentInit
from Products.CMFCore import permissions, DirectoryView
from Products.CMFCore.utils import registerIcon


from zope.i18nmessageid import MessageFactory
PloneGazetteFactory = MessageFactory('plonegazette')

## App imports
import NewsletterTheme, Newsletter, Subscriber, Section, NewsletterTopic
from config import PROJECTNAME
from config import product_globals

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/PloneGazette', product_globals)

## Types to register

contentConstructors = (Newsletter.addNewsletter, Subscriber.addSubscriber, NewsletterTopic.addNewsletterTopic)
contentClasses = (Newsletter.Newsletter, Subscriber.Subscriber, NewsletterTopic.NewsletterTopic)
factoryTypes = (Newsletter.Newsletter.factory_type_information,
                Subscriber.Subscriber.factory_type_information,
                NewsletterTopic.NewsletterTopic.factory_type_information)

## Patches to apply
import patches


def initialize(context):

    import NewsletterReference
    import NewsletterRichReference
    import NewsletterBTree

    ContentInit(
        'Plone Gazette Newsletter Theme',
        content_types = (NewsletterTheme.NewsletterTheme,),
        permission = PNLPermissions.AddNewsletterTheme,
        extra_constructors = (NewsletterTheme.addNewsletterTheme,),
        fti = NewsletterTheme.NewsletterTheme.factory_type_information).initialize(context)

    ContentInit(
        'Plone Gazette Newsletter Section',
        content_types = (Section.Section,),
        permission = PNLPermissions.ChangeNewsletter,
        extra_constructors = (Section.addSection,),
        fti = Section.Section.factory_type_information).initialize(context)

    ContentInit(
        'Plone Gazette resources',
        content_types = contentClasses,
        permission = permissions.AddPortalContent,
        extra_constructors = contentConstructors,
        fti = factoryTypes).initialize(context)

    registerIcon(NewsletterTheme.NewsletterTheme, 'skins/PloneGazette/NewsletterTheme.gif', globals())
    registerIcon(Newsletter.Newsletter, 'skins/PloneGazette/Newsletter.gif', globals())
    registerIcon(Subscriber.Subscriber, 'skins/PloneGazette/Subscriber.gif', globals())
    registerIcon(Section.Section, 'skins/PloneGazette/Section.gif', globals())
    registerIcon(NewsletterTopic.NewsletterTopic, 'skins/PloneGazette/NewsletterTopic.gif', globals())

    # Archetypes init
    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)

    ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = permissions.AddPortalContent,
        extra_constructors = constructors,
        fti = ftis,).initialize(context)

    return
