#!/usr/bin/env python

import genx
import sys

#Equivalent to hello.c

writer = genx.Writer()
fp = sys.stdout
writer.startDocFile(fp)
writer.startElementLiteral("greeting")
writer.addText("Hello world!")
writer.endElement()
writer.endDocument()

#arch-tag: simplest hello world sample
