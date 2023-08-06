import logging

from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName

from Products.Archetypes import Field

logger = logging.getLogger('collective.validationoverride')

orig_validate = Field.Field.validate

def validate(self, value, instance, errors=None, **kwargs):
    """
    Succeed and log errors if the user has the override permission
    """
    result = orig_validate(
        self, value, instance, errors=errors, **kwargs)
    if result and getToolByName(
        instance, 'portal_quickinstaller').isProductInstalled(
        'collective.validationoverride'
        ) and getSecurityManager().checkPermission(
        getattr(self, 'validation_override_permission',
                'Override validation'), instance):
        logger.warning(
            'Overriding the validation result %r on %r:\n%r'
            % (result, instance, errors))
        errors.pop(self.getName(), None)
        return
    return result
