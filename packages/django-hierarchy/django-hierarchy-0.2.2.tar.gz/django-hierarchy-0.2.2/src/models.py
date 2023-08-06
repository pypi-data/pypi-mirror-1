# -*- coding: utf-8 -*-
#
#  models.py
#  django-hierarchy
# 
#  Created by Lars Yencken on 09-11-2008.
#  Copyright 2008 Lars Yencken. All rights reserved.
#

"""
Database models for the django-hierarchy project.
"""

from django.db import models, connection

import model_tree

class HierarchicalModel(models.Model):
    "A generic hierarchical database model."

    left_visit = models.IntegerField(db_index=True)
    right_visit = models.IntegerField(db_index=True)

    class Meta:
        abstract = True

    @classmethod
    def get_root(cls):
        return cls.objects.get(left_visit=1)

    def get_ancestors(self):
        return self.__class__.objects.filter(
                left_visit__lte=self.left_visit,
                right_visit__gte=self.right_visit,
            ).order_by('left_visit')

    def get_subtree(self):
        return self.__class__.objects.filter(
                left_visit__gte=self.left_visit,
                right_visit__lte=self.right_visit,
            ).order_by('left_visit')

    def add_child(self, **kwargs):
        cls = self.__class__
        parent_left_visit = self.left_visit
        parent_right_visit = self.right_visit

        cursor = connection.cursor()
        cursor.execute("""
                UPDATE %s SET right_visit = right_visit + 2
                WHERE right_visit >= %%s
            """ % cls._meta.db_table, (parent_right_visit,))
        cursor.execute("""
                UPDATE %s SET left_visit = left_visit + 2
                WHERE left_visit > %%s
            """ % cls._meta.db_table, (parent_right_visit,))

        kwargs['left_visit'] = parent_right_visit
        kwargs['right_visit'] = parent_right_visit + 1
        new_node = cls(**kwargs)
        new_node.save()

        self.right_visit += 2
        return new_node

    def __cmp__(self, rhs):
        return cmp(self.left_visit, self.right_visit)

    def leaves(self):
        "Returns all leaf nodes under this node."
        return self.get_subtree().extra(
                where=['left_visit + 1 = right_visit'])
    
    def to_tree(self, label_field=None):
        """
        Fetches the entire subtree from the database, returning it as a 
        TreeNode structure.
        """
        if not label_field:
            if hasattr(self, 'label_field'):
                label_field = self.label_field
            else:
                raise ValueError('a label field must be specified')

        return model_tree.build_tree(self, label_field)
    
    def layout(self, label_field=None, method=None):
        "Pretty-prints the subtree rooted at this node."
        return self.to_tree(label_field=label_field).layout(method=method)

# vim: ts=4 sw=4 sts=4 et tw=78:

