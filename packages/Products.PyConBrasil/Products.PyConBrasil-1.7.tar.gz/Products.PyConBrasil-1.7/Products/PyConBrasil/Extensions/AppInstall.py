from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

def addToListProperty(self, out, propertySheet, property, value):
    """Add the given value to the list in the given property"""
    current = list(propertySheet.getProperty(property))
    if value not in current:
        current.append(value)
        propertySheet.manage_changeProperties(**{property : current})

    print >> out, "Added %s to %s" % (value, property)

def addFormControllerAction(self, out, controller, template, status,
                                contentType, button, actionType, action):
    """Add the given action to the portalFormController"""
    controller.addFormAction(template, status, contentType,
                                button, actionType, action)
    print >> out, "Added action %s to %s" % (action, template)

def install(self):

    out = StringIO()

    # Add catalog index/metadata
    catalog = getToolByName(self, 'portal_catalog')
    if 'UID' not in catalog.schema():
        catalog.addColumn('UID')
        print >> out, "[portal_catalog] Added 'UID' metadata column."
    if 'title_or_id' not in catalog.indexes():
        catalog.addIndex('title_or_id', 'FieldIndex')
        catalog.reindexIndex('title_or_id', None)

    # Set parentMetaTypesNotToQuery
    portalProperties = getToolByName(self, 'portal_properties')
    navtreeProps = getattr(portalProperties, 'navtree_properties')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'Inscricoes')

    # Set metaTypesNotToList
    addToListProperty(self, out, navtreeProps, 'metaTypesNotToList', 'Imprensa')
    addToListProperty(self, out, navtreeProps, 'metaTypesNotToList', 'Inscricao')
    addToListProperty(self, out, navtreeProps, 'metaTypesNotToList', 'PalestraRelampago')
    addToListProperty(self, out, navtreeProps, 'metaTypesNotToList', 'Palestra')
    addToListProperty(self, out, navtreeProps, 'metaTypesNotToList', 'Treinamento')

    # Set types_not_searched
    siteProps = getattr(portalProperties, 'site_properties')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'Inscricoes')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'Imprensa')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'Inscricao')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PalestraRelampago')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'Palestra')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'Treinamento')

    # Give the response types a "save" target to take the use back to the
    # issue itself, after updating the parent issue
    controller = getToolByName(self, 'portal_form_controller')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'Imprensa', None, 'traverse_to', 'string:imprensa_save')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'Inscricao', None, 'traverse_to', 'string:inscricao_save')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'PalestraRelampago', None, 'traverse_to', 'string:palestra_relampago_save')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'Palestra', None, 'traverse_to', 'string:palestra_save')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'Treinamento', None, 'traverse_to', 'string:treinamento_save')

    return out.getvalue()
