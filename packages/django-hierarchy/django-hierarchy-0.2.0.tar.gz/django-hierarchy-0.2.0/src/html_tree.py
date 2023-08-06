# -*- coding: utf-8 -*-
# 
#  html_tree.py
#  django-hierarchy
#  
#  Created by Lars Yencken on 2008-01-05.
#  Copyright 2008 Lars Yencken. All rights reserved.
# 

from tree import TreeNode

def default_annotator(node):
    label = node.label
    link = node.attrib.get('link')
    link_title = node.attrib.get('link_title')

    if link:
        if link_title:
            return '<a href="%s" title="%s">%s</a>' % (link, link_title,
                    label)
        else:
            return '<a href="%s">%s</a>' % (link, label)
    else:
        return label

def as_html_tree(tree, show_root=False, annotate=default_annotator, 
        open_until_depth=1):
    """Renders this map tree as an html tree."""
    if show_root:
        fake_root = TreeNode('root')
        fake_root.add_child(tree)
        return as_html_tree(fake_root, show_root=False, annotate=annotate)

    result = []
    result.append('<ul class="tree">')
    for child in sorted(tree.children.values()):
        result.append(_get_child_html(child, depth=1,
                open_until_depth=open_until_depth,
                annotate=annotate))
    result.append('</ul>')
    return '\n'.join(result)


def _get_child_html(node, depth, open_until_depth=1,
        annotate=default_annotator):
    result = []
    if depth >= open_until_depth:
        result.append('<li class="closed">')
    else:
        result.append('<li>')

    result.append(annotate(node))

    if node.children:
        result.append('<ul>')
        for child in sorted(node.children.values()):
            result.append(_get_child_html(child, depth+1, annotate=annotate,
                    open_until_depth=open_until_depth))
        result.append('</ul>')

    result.append('</li>')
    return ''.join(result)

