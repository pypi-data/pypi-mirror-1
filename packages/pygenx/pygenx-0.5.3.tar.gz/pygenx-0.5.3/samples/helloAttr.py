#!/usr/bin/env python

import genx
import sys

writer = genx.Writer()
writer.startDocFile(sys.stdout)
writer.startElementLiteral("greeting")
writer.addAttributeLiteral("type", "well-formed")
writer.addText("Hello world!")
writer.endElement()
writer.endDocument()

#arch-tag: python helloAttr script
