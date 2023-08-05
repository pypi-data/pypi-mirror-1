#!/usr/bin/env python

import genx

writer = genx.Writer()

fp = file("basic_example.xml", "w")

writer.startDocFile(fp)

writer.startElementLiteral("example")
writer.addText("This is an example")
writer.endElement()

writer.endDocument()
