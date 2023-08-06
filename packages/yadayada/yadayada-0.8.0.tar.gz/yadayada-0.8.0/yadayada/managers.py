from django.contrib.sites.managers import CurrentSiteManager
from django.db import models


class StdManager(models.Manager):

    def all_active(self):
        return self.filter(is_active=True)

    def by_sort_order(self, *args, **kwargs):
        sort_order = ['sort'] + list(args)
        return self.filter(**kwargs).order_by(sort_order)
