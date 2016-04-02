"""
    This layers only respond to whatsapp server notifications.
    Notifications can be a inform that the bot was added in a group, or someone was added to a group, or anything like that.
    Check yowsup.layers.protocol_groups.protocolentities for all notification protocol objects in Yowsup.

    Is this implementation we use the CreateGroupsNotificationProtocolEntity to check if the bot was
    added in a group, and leave if it is not allowed.
"""
import config
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_groups.protocolentities.iq_groups_leave import LeaveGroupsIqProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.iq_result_groups_list import ListGroupsResultIqProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups_add import AddGroupsNotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups_create import \
    CreateGroupsNotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups_remove import \
    RemoveGroupsNotificationProtocolEntity


class NotificationsLayer(YowInterfaceLayer):
    def __init__(self):
        super(NotificationsLayer, self).__init__()

    @ProtocolEntityCallback("notification")
    def onNotification(self, notification):
        """
            Reacts to any notification received
        """
        self.toLower(notification.ack())
        if isinstance(notification, CreateGroupsNotificationProtocolEntity):  # added on new group
            self.on_created_group(notification)
        elif isinstance(notification, ListGroupsResultIqProtocolEntity):  # result of a query of all groups
            self.on_groups_list(notification)
            # elif isinstance(notification, RemoveGroupsNotificationProtocolEntity):
            #     pass
            # elif isinstance(notification, AddGroupsNotificationProtocolEntity):
            #     pass

    def on_groups_list(self, listGroupResultEntity):
        groups = listGroupResultEntity.getGroups()
        for g in groups:
            if not self.is_allowed_on_group(g):
                self.leave_group(g)

    def on_created_group(self, createGroupsNotificationProtocolEntity):
        group_id = createGroupsNotificationProtocolEntity.getGroupId() + "@g.us"
        if self.is_allowed_on_group(createGroupsNotificationProtocolEntity):
            # this is a good place to a "Hello Group" message
            pass
        else:
            self.toLower(LeaveGroupsIqProtocolEntity(group_id))

    def is_allowed_on_group(self, group_entity):
        if config.filter_groups:
            isAllowed = False
            for jid, isAdmin in group_entity.getParticipants().iteritems():
                if jid.split("@")[0] in config.admins:
                    isAllowed = True
                    break
        else:
            isAllowed = True
        return isAllowed

    def leave_group(self, group_entity):
        group_id = group_entity.getGroupId() + "@g.us"
        self.toLower(LeaveGroupsIqProtocolEntity(group_id))
