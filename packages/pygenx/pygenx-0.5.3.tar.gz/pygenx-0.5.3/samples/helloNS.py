#!/usr/bin/env python

import genx
import sys

writer = genx.Writer()

writer.startDocFile(sys.stdout)
writer.startElementLiteral("greeting", "http://example.org/1")
writer.addAttributeLiteral("type", "well-formed", "http://example.com/zot")
writer.addText("\nHello world!")
writer.endElement()
writer.endDocument()

#arch-tag: hello namespace python script

