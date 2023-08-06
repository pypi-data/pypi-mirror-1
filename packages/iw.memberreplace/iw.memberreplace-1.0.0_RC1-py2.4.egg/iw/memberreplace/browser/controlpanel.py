## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file LICENSE.txt. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: controlpanel.py 81892 2009-03-07 23:35:10Z glenfant $
"""
MemberReplace control panel
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import transaction
from zope.interface import Interface, implements
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.schema import TextLine
from zope.schema import Bool
from zope.formlib import form
from zope.app.form.interfaces import WidgetInputError
from plone.app.controlpanel.form import ControlPanelForm
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from iw.memberreplace.utils import IwMemberReplaceMessageFactory as _
from iw.memberreplace.utils import logger
from iw.memberreplace.config import SUBTRANSACTION_THRESHOLD

class IMemberReplaceSchema(Interface):

    former_member = TextLine(
        title=_(u'label_former_member', default=u"Former member id"),
        description=_(u'help_former_member',
                      default=u"User id of the member to be replaced."),
        required=True)

    new_member = TextLine(
        title=_(u'label_new_owner', default=u"New member id"),
        description=_(u'help_new_owner',
                      default=u"User id of the member who will replace former member."),
        required=True)

    change_ownership = Bool(
        title=_(u'label_change_ownership', default=u"Replace in ownership"),
        description=_(u'help_change_ownership',
                      default=u"Replace in Zope owners of content items.")
        )

    change_creator = Bool(
        title=_(u'label_change_creator', default=u"Replace in creators"),
        description=_(u'help_change_creator',
                      default=u"Replace in DC creators of content items.")
        )

    change_sharings = Bool(
        title=_(u'label_change_sharings', default="Replace in sharings"),
        description=_(u'help_change_sharings',
                      default="Grant the same privileges in sharings.")
        )

    change_groups = Bool(
        title=_(u'label_change_groups', default="Replace in groups"),
        description=_(u'help_change_groups',
                      default=u"Replace in mutable groups. This doesn't work for groups provided by LDAP or a RDBMS.")
        )

    delete_former_member = Bool(
        title=_(u'label_delete_former_member', default=u"Delete former member?"),
        description=_(u'help_delete_former_member',
                      default=u"Delete former member after operation if its source is mutable?")
        )

    dry_run = Bool(
        title=_(u'label_dry_run', default="Dry run"),
        description=_(u'help_dry_run',
                      default=u"Just for testing if this can be achieved.")
        )

    log_process = Bool(
        title=_(u'label_log_process', default="Log changes"),
        description=_(u'help_log_process',
                      default=u"Writes details of the replacement process in the event log. Watch lines prefixed with 'iw.memberreplace'.")
        )


class MemberReplaceControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMemberReplaceSchema)

    def __init__(self, context):
        """Minimal adapter"""
        self.former_member = ''
        self.new_member = ''
        self.change_ownership = False
        self.change_creator = False
        self.change_sharings = False
        self.change_groups = False
        self.delete_former_member = False
        self.dry_run = False
        self.log_process = False
        return


class MemberReplaceControlPanel(ControlPanelForm):
    """Our control panel handler"""

    form_fields = form.FormFields(IMemberReplaceSchema)
    label = _(u'title_changing_member', default=u"Changing member")
    description = _(
        u'description_changing_member',
        default=u"Replacing an user by another across the site (might take some minutes on large sites)")
    form_name = _(u'title_changing_member', default=u"Changing member")


    def validate(self, action, data):

        # Perform default validation
        ret = super(MemberReplaceControlPanel, self).validate(action, data)

        # Check existing user ids
        error_fields = [x.field_name for x in ret]
        errors = []
        for user_field in ('former_member', 'new_member'):
            if user_field in error_fields:
                continue
            if not self._exists_user(data[user_field]):
                title_widget = self.widgets[user_field]
                error = WidgetInputError(
                    field_name=user_field,
                    widget_title=title_widget.label,
                    errors=_(
                        u'error_no_such_user',
                        default=u"No such user"))
                title_widget._error = error
                errors.append(error)

        # User ids must be different
        if len(errors) == 0 and (data['former_member'] == data['new_member']):
            for user_field in ('former_member', 'new_member'):
                title_widget = self.widgets[user_field]
                error = WidgetInputError(
                    field_name=user_field,
                    widget_title=title_widget.label,
                    errors=_(
                        u'error_duplicate_user',
                        default=u"User ids must be different"))
                title_widget._error = error
                errors.append(error)

        # Check if member can be deleted if deletion is selected
        if len(errors) == 0 and data['delete_former_member']:
            portal_membership = getMultiAdapter((self.context, self.request), name=u'plone_tools').membership()
            member = portal_membership.getMemberById(data['former_member'])
            if not member.canDelete():
                # FIXME: Waaaah! Noisy formlib API, didn't I make too much ?
                error = WidgetInputError(
                    field_name='delete_former_member',
                    widget_title=self.widgets['delete_former_member'].label,
                    errors=_(
                        u'error_cannot_delete_member',
                        default=u"Member cannot be deleted. Probably in a non mutable source."))
                self.widgets['delete_former_member']._error = error
                errors.append(error)

        # At least one change action must be checked
        one_checked = reduce(lambda x,y: x or y,
                             [data[k] for k in data.keys() if k.startswith('change_')])

        if not one_checked:
            title_widget = self.widgets['change_ownership']
            error = WidgetInputError(
                field_name='change_ownership',
                widget_title=title_widget.label,
                errors=_(
                    u'error_at_least_one_change',
                    default=u"You must select one or more change checkbox"))
            title_widget._error = error
            errors.append(error)

        return ret + errors


    def _exists_user(self, user_id):
        plone_state = getMultiAdapter((self.context, self.request),
                                     name=u'plone_portal_state')
        uf = plone_state.portal().acl_users
        return uf.getUserById(str(user_id)) is not None


    def _on_save(self, data=None):

        # Some shortcuts
        self._mustlog = data['log_process']
        really_run = not data['dry_run']
        former_member = str(data['former_member'])
        new_member = str(data['new_member'])
        plone_state = getMultiAdapter((self.context, self.request),
                                     name=u'plone_portal_state')
        uf = plone_state.portal().acl_users
        uf_path = '/'.join(uf.getPhysicalPath())[1:] # 'path/to/acl_users' no leading '/'
        new_user_ob = uf.getUserById(new_member)
        plone_tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        types_tool = plone_tools.types()
        valid_types = types_tool.listContentTypes()
        catalog = plone_tools.catalog()

        changes_count = 0
        # Looping in content (brains)
        for brain in catalog():
            changed = False
            brain_url = brain.getURL()

            # Filtering unprocessable items
            if brain.portal_type not in valid_types:
                continue
            item = brain.getObject()
            if item is None:
                self.log("Ghost object at %s, you should refresh the catalog", brain_url)
                continue

            # Technical ownership
            if data['change_ownership']:
                item_oi = item.owner_info()
                if (item_oi['explicit'] and (item_oi['id'] == former_member)
                    and (item_oi['path'] == uf_path)):
                    if really_run:
                        changed = True
                        item.changeOwnership(new_user_ob)
                    self.log("Changed ownership of %s", brain_url)

            # Creators
            if data['change_creator']:
                creators = item.Creators()
                if former_member in creators:
                    creators = list(creators)
                    i = creators.index(former_member)
                    creators[i] = new_member
                    if really_run:
                        changed = True
                        item.setCreators(creators)
                    self.log("Changed creators in %s", brain_url)

            # Sharings
            if data['change_sharings']:
                local_roles = item.get_local_roles_for_userid(former_member)
                if local_roles:
                    # former_member has local role(s) here
                    new_member_lr = item.get_local_roles_for_userid(new_member)
                    new_member_lr = list(set(new_member_lr) | set(local_roles))
                    if really_run:
                        changed = True
                        item.manage_delLocalRoles([former_member])
                        item.manage_addLocalRoles(new_member, new_member_lr)
                    self.log("Changed sharings in %s", brain_url)

            # Managing transaction and cataloging
            if changed:
                changes_count += 1
                catalog.reindexObject(item, idxs=['allowedRolesAndUsers', 'Creator'])

            if (changes_count > 0) and (changes_count % SUBTRANSACTION_THRESHOLD == 0):
                transaction.savepoint(optimistic=True)
                self.log("Committing subtransaction after %s items changed", changes_count)


        # Change in mutable groups
        if data['change_groups']:
            former_user_ob = uf.getUserById(former_member)
            portal_groups = getToolByName(self.context, 'portal_groups')
            for group_id in former_user_ob.getGroupIds():
                #for group_id in portal_groups.getGroupsForPrincipal(former_user_ob):
                group = uf.getGroupById(group_id)
                if not group.canAddToGroup(group_id):
                    self.log("Can't replace user in group %s, not mutable group", group_id)
                    continue
                if really_run:
                    portal_groups.removePrincipalFromGroup(former_member, group_id)
                    portal_groups.addPrincipalToGroup(new_member, group_id)
                self.log("Replaces %s with %s in group %s", former_member, new_member, group_id)

        # Remove former member
        if data['delete_former_member']:
            if really_run:
                portal_membership = plone_tools.membership()
                portal_membership.deleteMembers([data['former_member']], delete_memberareas=0, delete_localroles=1)
            self.log("Removed member %s", data['former_member'])

        self.log("Properties/ownership changed in %s object", changes_count)
        if not really_run:
            self.log("Dry run mode, aborting changes")
        return

    def log(self, text, *args):
        if self._mustlog:
            logger.info(text, *args)
        return
