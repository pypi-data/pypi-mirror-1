# -*- coding: utf-8 -*-
# 
#  tree.py
#  django-hierarchy
#  
#  Created by Lars Yencken on 2008-01-07.
#  Copyright 2008 Lars Yencken. All rights reserved.
# 

""" 
A generic interface to rebuild a tree in memory from any table which uses
the nested set abstraction.
"""

from django.db.models import fields

from tree import TreeNode

def build_tree(model_obj, label_field):
    """Constructs a tree out of the object fields."""
    _validateClass(model_obj.__class__)
    assert model_obj.pk and model_obj.left_visit and model_obj.right_visit

    subtree = model_obj.get_subtree()
    field_names = [f.name for f in model_obj.__class__._meta.fields]
    root_node = _build_tree(subtree, field_names, label_field)
    return root_node

def build_path(model_obj, label_field):
    _validateClass(model_obj.__class__)
    assert model_obj.pk and model_obj.left_visit and model_obj.right_visit
    nodes = model_obj.get_ancestors()
    field_names = [f.name for f in model_obj.__class__._meta.fields]
    root_node = _build_tree(nodes, field_names, label_field)
    return root_node

#----------------------------------------------------------------------------#

def _validateClass(model_class):
    getField = model_class._meta.get_field
    left_visit_field = getField('left_visit')
    right_visit_field = getField('right_visit')
    assert isinstance(left_visit_field, fields.IntegerField)
    assert isinstance(right_visit_field, fields.IntegerField)
    return

def _build_tree(subtree, field_names, label_field):
    db_obj_iter = iter(subtree)
    ancestors = [_build_node(db_obj_iter.next(), field_names, label_field)]
    for db_obj in db_obj_iter:
        while db_obj.left_visit < ancestors[-1].attrib['left_visit'] or \
                db_obj.right_visit > ancestors[-1].attrib['right_visit']:
            ancestors.pop()
        node = _build_node(db_obj, field_names, label_field)
        ancestors[-1].add_child(node)
        ancestors.append(node)

    return ancestors[0]

def _build_node(db_obj, field_names, label_field):
    node = TreeNode(getattr(db_obj, label_field))
    for field_name in field_names:
        node.attrib[field_name] = getattr(db_obj, field_name)

    return node

#----------------------------------------------------------------------------#
