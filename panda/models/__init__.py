#!/usr/bin/env python

from django.contrib.auth.models import Group, User
from django.db import models
from django.dispatch import receiver
from tastypie.models import ApiKey

from panda import config # Needed for autodiscovery
from panda.models.activity_log import ActivityLog
from panda.models.category import Category
from panda.models.dataset import Dataset
from panda.models.data_upload import DataUpload
from panda.models.export import Export
from panda.models.notification import Notification 
from panda.models.related_upload import RelatedUpload
from panda.models.search_log import SearchLog
from panda.models.task_status import TaskStatus
from panda.models.user_profile import UserProfile

__all__ = ['ActivityLog', 'Category', 'Dataset', 'DataUpload', 'Export', 'Notification', 'RelatedUpload', 'SearchLog', 'TaskStatus', 'UserProfile']

@receiver(models.signals.post_save, sender=User)
def on_user_post_save(sender, instance, created, **kwargs):
    """
    When a User is created, create an API key for them,
    add them to the panda_user group and send them an activation email.
    When a User is saved, update their Datasets' metadata in Solr. 
    """
    # Setup activation
    if created and not kwargs.get('raw', False):
        ApiKey.objects.get_or_create(user=instance)

        panda_users = Group.objects.get(name='panda_user')
        instance.groups.add(panda_users)

        user_profile = UserProfile(user=instance)
        user_profile.generate_activation_key()
        user_profile.save()

        user_profile.send_activation_email()

