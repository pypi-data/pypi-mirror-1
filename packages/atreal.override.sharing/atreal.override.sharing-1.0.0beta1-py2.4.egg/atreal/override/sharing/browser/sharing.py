from zope.component import queryUtility
from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize.instance import memoize

from atreal.override.sharing.browser.controlpanel import IOverrideSharingSchema
from atreal.override.sharing import OverrideSharingMessageFactory as _

class OverrideSharingView(BrowserView):
    """
    """
    
    def test(self, a, b, c):
        """
        """
        if a:
            return b
        else:
            return c

    @property
    def _options(self):
        """
        """
        _siteroot = queryUtility(IPloneSiteRoot)
        return IOverrideSharingSchema(_siteroot)

    @property
    def groups(self):
        """ Return list of groups available in controlpanel
        """
        return getattr(self._options, 'sharing_group_confidential', []) 

    @property
    def inherited(self):
        """ Return the value for inherited local roles : True if not herits
        """
        return getattr(self.context, '__ac_local_roles_block__', None)
    
    @property
    def restricted(self):
        """ Return the value for the restricted checkbox
        """
        if self.inherited :
            return True
        return None
    
    @memoize
    def existing_role_settings(self):
        """
        """
        #
        acl_users = getToolByName(self.context, 'acl_users')
        local_roles = acl_users._getLocalRolesForDisplay(self.context)      
        #
        info = []
        for name, roles, rtype, rid in local_roles:
            if rtype == 'group' and 'Reader' in roles:
                info.append(rid)
        #
        info.sort()
        return info

    def checkForm(self):
        """
        """
        # if form is not submitted return
        if not self.request.has_key('form.button.apply'):
            return
        
        #
        reindex = None
        
        #
        if self.request.has_key('restrict_access'):
            # Checkbox is checked
            if not self.inherited:
                # We have to change inherited attribute
                self.context.__ac_local_roles_block__ = True
                reindex = True
        else:
            # Checkbox is not checked
            if self.inherited:
                # We have to change inherited attribute
                self.context.__ac_local_roles_block__ = None
                reindex = True
        
        # List of groups checked in form
        groups_checked = []
        if self.request.has_key('groups'):
            groups_checked = self.request.form['groups']
        if isinstance(groups_checked, basestring):
            groups_checked = [groups_checked,]
        groups_checked.sort()
        
        #
        dict = self.context.__ac_local_roles__
        for group in self.groups:
            if group in groups_checked:
                if group not in self.existing_role_settings():
                    #  We have to add the local role
                    if dict.has_key(group):
                        self.context.manage_addLocalRoles(group, ['Reader',])
                    else:
                        self.context.manage_setLocalRoles(group, ['Reader',])
                    reindex = True
            else:
                if group in self.existing_role_settings():
                    # We have to delete the local role
                    local_roles = dict.get(group, [])
                    if local_roles == ['Reader',]:
                        self.context.manage_delLocalRoles(userids=[group,])
                    else:
                        local_roles.remove('Reader')
                        self.context.manage_setLocalRoles(group, local_roles)
                    reindex = True
        
        #
        if reindex:
            self.context.reindexObjectSecurity()
            status = _(u"Changes saved.")
        else:
            status = _(u"No changes made.")
        
        # Status message
        self.request.response.redirect(self.context.absolute_url()+'/@@overridesharing')
        IStatusMessage(self.request).addStatusMessage(status,type='info')
        return
