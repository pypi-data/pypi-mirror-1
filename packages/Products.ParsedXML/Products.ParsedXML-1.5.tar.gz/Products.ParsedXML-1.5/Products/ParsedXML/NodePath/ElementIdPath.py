##############################################################################
#
# Copyright (c) 2001-2004 Zope Corporation and Contributors. All
# Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from NodePath import BaseNodePathScheme, registry

class ElementIdPathScheme(BaseNodePathScheme):
    def __init__(self, scheme_name=None):
        scheme_name = scheme_name or 'element_id'
        BaseNodePathScheme.__init__(self, scheme_name)

    def resolve_steps(self, top_node, steps):
        node = top_node
        for step in steps:
            if step[0] == 'e':
                element_id = int(step[1:])
                for child in node.childNodes:
                    if self.get_element_id(child) == element_id:
                        node = child
                        break
                else:
                    # couldn't find node with such element_id
                    return None
            else:
                node = node.childNodes.item(int(step))
                if node is None:
                    return None
        return node # return node

    def create_steps(self, top_node, node):
        steps = []
        while node is not top_node:
            parent = node.parentNode
            if parent is None:
                break
            element_id = self.get_element_id(node)
            if element_id != -1:
                steps.append("e%s" % element_id)
            else:
                steps.append(str(parent.childNodes.index(node)))
            node = parent
        steps.reverse()
        return steps

    def get_element_id(self, node):
        return getattr(node, 'elementId', -1)

