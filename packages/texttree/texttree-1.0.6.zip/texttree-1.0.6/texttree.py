"""Parse textual representations of trees.

Parse textual representations of trees using indentation to show nesting.

"""

# Copyright (c) 2009, Tom Wright All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.  
# 
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of  conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.  

#     * Neither the name of Tom Wright nor the names of his contributors
#       may be used to endorse
#       or promote products derived from this software without specific prior
#       written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from itertools import takewhile


__all__ = ["build_tree", "Tree"]

def indent(txt, stops=1):
    return '\n'.join(" " * 4 * stops + line
        for line in  txt.splitlines())

def leading_spaces(string):
    return len(list(takewhile(' '.__eq__, string)))


class Tree(object):
    """Minimal class representing a tree. 
    
    Has comparison and formatting functions."""

    def __init__(self, value, children):
        self.value = value
        self.children = children


    def __repr__(self):
        childrenRepr = indent(repr(self.children))
        return "Tree(%r, %s)" % (self.value, childrenRepr)


    def __eq__(self, other):
        return self.value == other.value and self.children == other.children


    def __neq__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        if self.children:
            childString = "\n" + indent('\n'.join(str(child) for child in self.children))
        else:
            childString = ""
        return "%s%s" % (self.value, childString)
                                        

def build_tree(lines):
    """Parse a string representation of a tree.
    
    The string should consist of indented lines, where the level of 
    indentation indicates nesting. Returns a tree object with strings for
    values. Any leading whitespace or indentation is ignored, any trailing
    whitespace is stripped."""
    forest = build_forest(lines)
    if len(forest) == 0:
        raise Exception("Empty tree")
    elif len(forest) > 1:
        raise Exception("Several root nodes")
    return forest[0]
    

def build_forest(lines):
    if isinstance(lines, str):
        lines = strip_whitespace(lines.splitlines())

    if not lines:
        return []
    return [Tree(head, build_forest(sub_lines)) for (head, sub_lines) in 
        split_groups(lines)]


def split_groups(lines):
    lines = strip_indent(lines)
    if lines == []:
        return []
    if leading_spaces(lines[0]) != 0:
        raise Exception("Inconsistent indentation on line: %s" % lines[0])
    roots = [i for (i, line) in enumerate(lines) if leading_spaces(line) == 0]
    regions = zip(roots, roots[1:] + [len(lines)])
    return [(lines[start], lines[start + 1: end]) for (start, end) in regions]


def strip_whitespace(lines):
    lines = filter(lambda x: not set(x) <= set([' ']), lines)
    lines = map(str.rstrip, lines)
    return lines


def strip_indent(lines):
    if not lines:
        return lines
    indent = min(leading_spaces(line) for line in lines)
    lines = [line[indent:] for line in lines]
    return lines

