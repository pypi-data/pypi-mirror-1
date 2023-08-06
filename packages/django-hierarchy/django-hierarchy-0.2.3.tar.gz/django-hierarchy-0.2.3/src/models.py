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
from django.conf import settings
from itertools import dropwhile

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
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
        return self.__class__.objects.filter(
                left_visit__lte=self.left_visit,
                right_visit__gte=self.right_visit,
            ).order_by('left_visit')

    def get_children(self):
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
        valid_children = []
        subtree_nodes = iter(self.get_subtree())
        parent = subtree_nodes.next()
        try:
            while True:
                node = subtree_nodes.next()
                valid_children.append(node)
                subtree_nodes = dropwhile(
                        lambda n: n.right_visit < node.right_visit,
                        subtree_nodes
                    )
        except StopIteration:
            pass
        return valid_children

    def get_subtree(self):
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
        return self.__class__.objects.filter(
                left_visit__gte=self.left_visit,
                right_visit__lte=self.right_visit,
            ).order_by('left_visit')

    def add_child(self, **kwargs):
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
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

    def refresh_position(self):
        """
        Fetches an authoritative position of this node in the tree from the
        database. This is very important to do when the tree has been
        modified, otherwise tree-based operations have undefined results.
        Returns true if the node was out of date, False otherwise.
        """
        cls = self.__class__
        record = cls.objects.values('left_visit', 'right_visit').get(
                pk=self.pk)
        was_dirty = False
        if self.left_visit != record['left_visit']:
            self.left_visit = record['left_visit']
            was_dirty = True

        if self.right_visit != record['right_visit']:
            self.right_visit = record['right_visit']
            was_dirty = True

        return was_dirty

    def __cmp__(self, rhs):
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
        return cmp(self.left_visit, rhs.right_visit)

    def leaves(self):
        "Returns all leaf nodes under this node."
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
        return self.get_subtree().extra(
                where=['left_visit + 1 = right_visit'])
    
    def to_tree(self, label_field=None):
        """
        Fetches the entire subtree from the database, returning it as a 
        TreeNode structure.
        """
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
        if not label_field:
            if hasattr(self, 'label_field'):
                label_field = self.label_field
            else:
                raise ValueError('a label field must be specified')

        return model_tree.build_tree(self, label_field)
    
    def layout(self, label_field=None, method=None):
        "Pretty-prints the subtree rooted at this node."
        if settings.DEBUG:
            assert not self.refresh_position(), "node was out of date"
        return self.to_tree(label_field=label_field).layout(method=method)

# vim: ts=4 sw=4 sts=4 et tw=78:
