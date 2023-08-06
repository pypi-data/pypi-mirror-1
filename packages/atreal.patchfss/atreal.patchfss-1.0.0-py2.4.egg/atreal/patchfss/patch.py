import logging
logger = logging.getLogger('atreal.patchfss')
LOG = logger.info

import os

from Products.CMFCore.utils import ContentInit
from Products.CMFCore import permissions as CCP

from Products.Archetypes.public import process_types, listTypes

from Products.CMFEditions.Modifiers import ConditionalTalesModifier

from iw.fss.modifier import manage_addModifier
from iw.fss.modifier import modifierAddForm
from iw.fss.modifier import MODIFIER_ID

def initialize(context):

    from iw.fss.config import PROJECTNAME
    from iw.fss.customconfig import (ZOPETESTCASE,
                                     INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE)

    if ZOPETESTCASE or os.environ.get(INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE):
        # Import example types
        from iw.fss import examples
        dummy = examples # No pyflakes warning
        content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                          PROJECTNAME)
        ContentInit('%s Content' % PROJECTNAME,
                    content_types = content_types,
                    permission = CCP.AddPortalContent,
                    extra_constructors = constructors,
                    fti = ftis,
                    ).initialize(context)


    # Register modifier
    context.registerClass(
        ConditionalTalesModifier,
        MODIFIER_ID,
        permission=CCP.ManagePortal,
        constructors = (modifierAddForm, manage_addModifier),
        icon='modifier.gif',
        )

    # Setup module aliases to bind all Zope2 products
    from iw.fss import modulealiases
    dummy = modulealiases # No pyflakes warning

    LOG("Monkey patching iw.fss.initialize with atreal.patchfss.patch.initialize")
    # Provides 'plone' domain translations
    #if not ZOPETESTCASE:
        #i18n_dir = os.path.join(os.path.dirname(__file__), 'i18n')
        #context._ProductContext__app.Control_Panel.TranslationService._load_i18n_dir(i18n_dir)

    return
