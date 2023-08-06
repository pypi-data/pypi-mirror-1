from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.public import StringField, SelectionWidget, DisplayList
from Products.CMFCore.permissions import ChangeLocalRoles
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.browser.search import PASSearchView as passearch
import sets


class RoleField(StringField):
    """ An Archetypes field that manages local roles.
    """
    
    _properties = StringField._properties.copy()

    _properties.update({
        'type': 'role',
        'multiValued': True,
        'write_permission': ChangeLocalRoles,
        'widget': SelectionWidget,
        'role': None,                   # The local role that will be assigned.
        'target_expression': None,      # An expression returning the 
                                        # target object where local roles should be 
                                        # assigned. If None, context will be used as target.
        'allow_protected_roles': False, # Allow the user to change protected roles 
                                        # for himself.
        'protected_roles': ('Manager', 'Owner'),
                                        # Roles that a user shouldn't be able to change 
                                        # for himself, if 'allow_protected_roles' is True.
        'filter_groups': None,          # Filter users/groups by group. If None, no 
                                        # filter is made. Only used if vocabulary is 
                                        # None and so the default vocabulary is used.
        'principals': 'users',          # Possible values are 'users', 'groups' and 'all'.
                                        # Only used if 'vocabulary' is 
                                        # None and so the default vocabulary is used.
    })

    security  = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        target = self.getTarget(instance)
        users = target.users_with_local_role(self.role)
        
        if self.multiValued:
            return list(users)
        
        # FIXME raise error if len(users)>1 ?
        if users:
            return users[0]


    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):

        target = self.getTarget(instance)

        if isinstance(value, type('')):
            value = [value]

        protected_roles = not self.checkProtectedRoles()
        
        # remove deleted roles.
        previous_value = target.users_with_local_role(self.role)
        users_remove = [u for u in previous_value if u not in value]

        for userid in users_remove:
            if protected_roles and self._checkUser(instance, userid):
                continue
            user_roles = list(target.get_local_roles_for_userid(userid))
            user_roles.remove(self.role)
            if user_roles:
                target.manage_setLocalRoles(userid, user_roles)
            else:
                target.manage_delLocalRoles([userid])

        # set new roles

        for userid in value:
            if protected_roles and self._checkUser(instance, userid):
                continue
            user_roles = list(target.get_local_roles_for_userid(userid))
            if self.role not in user_roles:
                user_roles.append(self.role)
                target.manage_setLocalRoles(userid, user_roles)


    security.declarePrivate('getTarget')
    def getTarget(self, instance):
        """ Get the target object where local roles should be assigned.
        """
        if self.target_expression:
            return eval(self.target_expression, {'context': instance, 'here' : instance})
        return instance


    security.declarePrivate('checkProtectedRoles')
    def checkProtectedRoles(self):
        if self.allow_protected_roles:
            return True

        if self.role not in self.protected_roles:
            return True

        return False


    security.declarePrivate('_checkUser')
    def _checkUser(self, instance, userid):        
        ms_tool = getToolByName(instance, 'portal_membership')
        if ms_tool.isAnonymousUser():
            return False
        
        member_id = ms_tool.getAuthenticatedMember().getId()
        if member_id == userid:
            return True
        
        return False


    def getDefault(self, instance):
        default = StringField.getDefault(self, instance)

        if not default:
            # ensure we don't break the owner role during initialization.
            default = instance.users_with_local_role(self.role)

        return default

    def Vocabulary(self, content_instance=None):
        vocabulary = StringField.Vocabulary(self, content_instance=content_instance)

        if vocabulary or (content_instance is None):
            return vocabulary

        # no vocabulary defined, try to get a list of users.
        acl_users = getToolByName(content_instance, 'acl_users')

        vocab_users = []
        
        if self.principals == 'users':
            if self.filter_groups:
                users = []
                for groupid in self.filter_groups:
                    groupobj = acl_users.getGroup(groupid)
                    group_member_ids = groupobj.getMemberIds()
                    users.extend([acl_users.searchUsers(id=userid)[0] for userid in group_member_ids])
            else:
                users = acl_users.searchUsers()
            vocab_users = [(u['userid'], u['title']) for u in users]

        elif self.principals == 'groups':
            vocab_users = [(u['groupid'], u['title']) for u in acl_users.searchGroups()]
        
        elif self.principals == 'all':
            users = [(u['userid'], u['title']) for u in acl_users.searchUsers()]
            groups = [(u['groupid'], u['title']) for u in acl_users.searchGroups()]
            vocab_users = users + groups
                
        
        return DisplayList(list(sets.Set(vocab_users)))


registerField(RoleField, title='Role', description='Used to set local roles.')
registerPropertyType('role', 'string', RoleField)
registerPropertyType('target_expression', 'string', RoleField)
registerPropertyType('allow_protected_roles', 'lines', RoleField)
registerPropertyType('protected_roles', 'lines', RoleField)