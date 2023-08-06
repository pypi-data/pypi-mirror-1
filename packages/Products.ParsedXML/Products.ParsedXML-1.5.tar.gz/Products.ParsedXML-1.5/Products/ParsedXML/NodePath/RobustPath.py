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

from NodePath import BaseNodePathScheme, NodePathError
import random, string, urllib
import xml.dom

words_amount = 5

class RobustPathScheme(BaseNodePathScheme):
    def __init__(self):
        BaseNodePathScheme.__init__(self, 'robust')

    def resolve_steps(self, top_node, steps):
        steps, type_step, context_step = steps[:-2], steps[-2], steps[-1]
        rsteps = []
        # create element steps
        for step in steps:
            nodeName, nodeIndex = string.split(step, "*")
            rsteps.append(GenericStep(xml.dom.Node.ELEMENT_NODE,
                                      nodeName, int(nodeIndex)))
        # now create type and context end steps
        context_parts = string.split(context_step, "*")
        node_type, nodeIndex = string.split(type_step, "*")
        nodeIndex = int(nodeIndex)
        if node_type == 'element':
            type_rstep = GenericStep(xml.dom.Node.ELEMENT_NODE,
                                context_parts[0], nodeIndex)
            context_rstep = ElementEndStep(int(context_parts[1]),
                                           int(context_parts[2]))
        elif node_type == 'text':
            type_rstep = GenericStep(xml.dom.Node.TEXT_NODE,
                                     "#text", nodeIndex)
            words = []
            for i in range(0, len(context_parts), 2):
                words.append((urllib.unquote(context_parts[i]),
                             int(context_parts[i + 1])))
            context_rstep = TextEndStep(words)
        elif node_type == 'empty':
            type_rstep = GenericStep(xml.dom.Node.TEXT_NODE,
                                     "#text", nodeIndex)
            context_rstep = EmptyTextEndStep()
        elif node_type == 'other':
            raise NodePathError, "Cannot handle other path elements yet."
        else:
            raise NodePathError, "Unknown step type in path: %s" % node_type

        rsteps.append(type_rstep)
        rsteps.append(context_rstep)

        # resolve the steps, starting with step 0
        context = Context(0, rsteps)
        node, level = rsteps[0].resolve(context, top_node, 0)
        return node
        
    def create_steps(self, top_node, node):
        # first create last two steps
        parent = node.parentNode
        steps = self.create_end_steps(parent, node)
        node = parent
        # now create element steps
        while node is not top_node:
            parent = node.parentNode
            if parent is None:
                break
            steps.append(self.create_element_step(parent, node))
            node = parent
        steps.reverse()
        return steps
    
    def create_end_steps(self, parent, node):
        nodeType = node.nodeType
        if nodeType == node.ELEMENT_NODE:
            return ['%s*%s*%s' % (node.nodeName,
                                  len(node.attributes),
                                  len(node.childNodes)),
                    'element*%s' % parent.childNodes.index(node) ]
        elif nodeType == node.TEXT_NODE:
            if string.strip(node.data) == '':
                return ['empty',
                        'empty*%s' % parent.childNodes.index(node)]
            else:
                return [string.join(get_words_sample(node.data), "*"),
                        'text*%s' % parent.childNodes.index(node)]
        else:
            # FIXME: simplistic way to deal with other nodes
            return ['%s' % node.nodeType,
                    'other*%s' % parent.childNodes.index(node)]
        
    def create_element_step(self, parent, node):
        return "%s*%s" % (node.nodeName, parent.childNodes.index(node))
    
class Context:
    threshold = 30
    success_threshold = 10
    offset_unreliability = 3
    tree_skip_unreliability = 3
    step_skip_unreliability = 3
    word_max_distance = 7
    word_offset_unreliability = 2
    
    def __init__(self, i, steps):
        self._i = i
        self._steps = steps
            
    def resolve_next(self, node, level):
        steps = self._steps
        i = self._i + 1
        if i < len(steps):
            # prepare new context for next step
            context = Context(i, steps)
            # resolve the next step
            return steps[i].resolve(context, node, level)
        else:
            return node, level

class GenericStep:
    def __init__(self, nodeType, nodeName, index):
        self._nodeType = nodeType
        self._nodeName = nodeName
        self._index = index
    
    def resolve(self, context, node, level):
        nodeType = self._nodeType
        nodeName = self._nodeName
        i = self._index
        childNodes = node.childNodes
        l = len(childNodes)

        results = []
        # try if the indicate node is the one, if so, return it
        if i < l:
            current = childNodes[i]
            if (current.nodeType == nodeType and
                current.nodeName == nodeName):
                 current_node, current_unreliability = context.resolve_next(
                     current, level)
                 if current_unreliability < context.success_threshold:
                     return current_node, current_unreliability
                 results.append((current_node, current_unreliability))
            # we need to go forward and backward from position i
            forward_i = i + 1
            backward_i = i - 1
            can_go_forward = can_go_backward = 1
        else:
            # i is beyond length, so we need to go backward from end
            backward_i = l - 1
            forward_i = l
            can_go_forward = 0
            can_go_backward = 1

        # try nodes forward and backward of this one
        unreliability = level + context.offset_unreliability
        while ((can_go_forward or can_go_backward) and
               unreliability < context.threshold):
            if forward_i < l:
                current = childNodes[forward_i]
                if (current.nodeType == nodeType and
                    current.nodeName == nodeName):
                    current_node, current_unreliability = context.resolve_next(
                        current, unreliability)
                    if current_unreliability < context.success_threshold:
                        return current_node, current_unreliability
                    results.append((current_node, current_unreliability))
                forward_i = forward_i + 1
            else:
                can_go_forward = 0
                
            if backward_i >= 0:
                current = childNodes[backward_i]
                if (current.nodeType == nodeType and
                    current.nodeName == nodeName):
                    current_node, current_unreliability = context.resolve_next(
                        current, unreliability)
                    if current_unreliability < context.success_threshold:
                        return current_node, current_unreliability
                    results.append((current_node, current_unreliability))   
                backward_i = backward_i - 1
            else:
                can_go_backward = 0

            unreliability = unreliability + context.offset_unreliability

        # try skipping level in the tree
        unreliability = level + context.tree_skip_unreliability
        if unreliability < context.threshold:
            for current in childNodes:
                # use same step but with next nodes
                current_node, current_unreliability = self.resolve(
                    context, current, unreliability)
                if current_unreliability < context.success_threshold:
                    return current_node, current_unreliability
                results.append((current_node, current_unreliability))  

        # try skipping this step
        # use same node but with next step
        unreliability = level + context.step_skip_unreliability
        if unreliability < context.threshold:
            current_node, current_unreliability = context.resolve_next(
                node, unreliability)
            if current_unreliability < context.success_threshold:
                return current_node, current_unreliability
            results.append((current_node, current_unreliability))
            
        # no immediate success, so try the best branch
        best_unreliability = context.threshold
        best_node = None
        for found_node, found_unreliability in results:
            if found_unreliability < best_unreliability:
                best_unreliability = found_unreliability
                best_node = found_node
        return best_node, best_unreliability
    
class ElementEndStep:
    """Not very robust, but representable in a url pretty easily.
    """
    def __init__(self, attributeAmount, childAmount):
        self._attributeAmount = attributeAmount
        self._childAmount = childAmount

    def resolve(self, context, node, level):
        if node.nodeType != node.ELEMENT_NODE:
            return None, context.threshold
        if (len(node.attributes) != self._attributeAmount or 
            len(node.childNodes) != self._childAmount):
            return None, context.threshold
        return node, level

class EmptyTextEndStep:
    
    def resolve(self, context, node, level):
        if node.nodeType != node.TEXT_NODE:
            return None, context.threshold
        if string.strip(node.data) == "":
            return node, level
        return None, context.threshold
    
class TextEndStep:
    def __init__(self, words):
        self._words = words
   
    def resolve(self, context, node, level):
        if node.nodeType != node.TEXT_NODE:
            return None, context.threshold
        words = string.split(node.data)
        if len(words) == 0:
            return None, context.threshold

        unreliability = level
        for word, nr in self._words:
            unreliability = unreliability + (
                find_word_distance(words, word, nr,
                                   context.word_max_distance) *
                context.word_offset_unreliability )
            if unreliability >= context.threshold:
                return None, context.threshold
        return node, unreliability

def find_word_distance(words, word, i, max_distance):
    """Find distance of word in words from expected location i.
    If word could not be found or is further than max_distance, return -1.
    """
    try:
        if words[i] == word:
            return 0
    except IndexError:
        l = len(words)
        distance = i - l + 1
        forward_i = l
        backward_i = l - 1
        can_go_forward = 0
        can_go_backward = 1
    else:
        l = len(words)
        distance = 1
        forward_i = i + 1
        backward_i = i - 1
        can_go_forward = can_go_backward = 1
    while (can_go_forward or can_go_backward) and (distance < max_distance):
        if forward_i < l:
            if words[forward_i] == word:
                return distance
            forward_i = forward_i + 1
        else:
            can_go_forward = 0
        if backward_i >= 0:
            if words[backward_i] == word:
                return distance
            backward_i = backward_i - 1
        else:
            can_go_backward = 0

        distance = distance + 1

    return max_distance

def get_words_sample(text,
                     words_amount=words_amount,
                     quote=urllib.quote):
    words = string.split(text)
    result = []

    if len(words) <= words_amount:
        # get all words if there are only a few
        for i in range(len(words)):
            # don't add any words with separator in it, so as not to confuse
            if "*" not in words[i] and "," not in words[i]:
                qword = quote(words[i])
                result.append(qword + "*" + str(i))
    else:
        # otherwise, take a random sample of words from the text
        nrs = []
        l = len(words) - 1
        for i in range(words_amount):
            while 1:
                r = random.randint(0, l)
                # if we selected new word from sample, done
                # NOTE: would introduce subtle bug if we checked for
                # * or , here
                if r not in nrs:
                    break
            nrs.append(r)
        nrs.sort()
        for nr in nrs:
            # don't want any word with separator in it
            if "*" not in words[nr] and "," not in words[nr]:
                qword = quote(words[nr])
                result.append(qword + "*" + str(nr))
    return result
