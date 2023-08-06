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

import string

class NodePathError(Exception):
    pass

class NodePathSchemeRegistry:
    def __init__(self):
        self._schemes = {}
        
    def register_scheme(self, scheme):
        self._schemes[scheme._scheme_name] = scheme

    def resolve_steps(self, top_node, steps, scheme_name):
        """Resolve steps from top_node.
        """
        # if we don't know scheme, return None as node could not be found
        if not self._schemes.has_key(scheme_name):
            raise NodePathError, "Unknown scheme: %s" % scheme_name 
        # we do know the scheme, so look it up
        scheme = self._schemes[scheme_name]
        # now resolve steps using this scheme
        return scheme.resolve_steps(top_node, steps)
    
    def resolve_path(self, top_node, path):
        """Resolve path.
        """
        if not path:
            return top_node
        steps = string.split(path, ',')
        # get scheme as first element of path
        scheme_name, steps = steps[0], steps[1:]
        # resolve steps using scheme
        return self.resolve_steps(top_node, steps, scheme_name)

    def create_steps(self, top_node, node, scheme_name):
        """Construct steps tuple to node.
        """
        return self._schemes[scheme_name].create_steps(top_node, node)
    
    def create_path(self, top_node, node, scheme_name):
        """Construct path to node according to scheme_name.
        """
        steps = self.create_steps(top_node, node, scheme_name)
        if not steps:
            return '' 
        return '%s,%s' % (scheme_name, string.join(steps, ','))

class BaseNodePathScheme:
    def __init__(self, scheme_name):
        self._scheme_name = scheme_name
    
    def resolve_steps(self, top_node, steps):
        """Resolve path from top_node, return node found or None.
        Steps are in order top_node to node.
        """
        pass

    def create_steps(self, top_node, node):
        """Return list of steps from top_node to node.
        Steps returned are in reverse order.
        """
        pass
    
class ChildNodePathScheme(BaseNodePathScheme):
    def __init__(self):
        BaseNodePathScheme.__init__(self, 'child')
        
    def resolve_steps(self, top_node, steps):
        node = top_node
        for step in steps:
            node = node.childNodes.item(int(step))
            if node is None:
                return None
        return node # return node

    def create_steps(self, top_node, node):
        steps = []
        # FIXME: is it safe to compare nodes like this?
        while node is not top_node:
            parent = node.parentNode
            if parent is None:
                break
            # FIXME: can index() be used in all python DOMs?
            steps.append(str(parent.childNodes.index(node)))
            node = parent
        steps.reverse()
        return steps

# create the registry
registry = NodePathSchemeRegistry()
