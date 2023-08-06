# -*- coding: utf-8 -*-
#$HeadURL: http://rst2pdf.googlecode.com/svn/tags/0.10.1/rst2pdf/utils.py $
#$LastChangedDate: 2009-05-16 01:46:20 +0200 (Sa, 16. Mai 2009) $
#$LastChangedRevision: 533 $

import shlex

from reportlab.platypus import Spacer

from flowables import *


def parseRaw (data):
    """Parse and process a simple DSL to handle creation of flowables.

    Supported (can add others on request):

    * PageBreak

    * Spacer width, height

    """
    elements = []
    lines = data.splitlines()
    for line in lines:
        lexer = shlex.shlex(line)
        lexer.whitespace += ','
        tokens = list(lexer)
        command = tokens[0]
        if command == 'PageBreak':
            if len(tokens) == 1:
                elements.append(MyPageBreak())
            else:
                elements.append(MyPageBreak(tokens[1]))
        if command == 'Spacer':
            elements.append(Spacer(int(tokens[1]), int(tokens[2])))
        if command == 'Transition':
            elements.append(Transition(*tokens[1:]))
    return elements


# Looks like this is not used anywhere now:
# def depth(node):
#    if node.parent == None:
#        return 0
#    else:
#        return 1 + depth(node.parent)
