#!/usr/bin/env python

import genx
import sys
import random
random.seed(234258243985) #not too concerned about randomness

def main():
    writer = genx.Writer()
    ns = writer.declareNamespace("http://example.org/dd", "dd")
    dates = writer.declareElement("dates", ns)
    date = writer.declareElement("date")
    yyyy = writer.declareAttribute("yyyy")
    mm = writer.declareAttribute("mm")

    writer.startDocFile(sys.stdout)
    writer.startElement(dates)
    writer.addText("\n")

    for i in range(0, 1000000):
        year = "%d" % (1900 + random.randrange(100))
        month = "%02d" % random.randrange(12)
        writer.startElement(date)
        writer.addAttribute(yyyy, year)
        writer.addAttribute(mm, month)
        writer.endElement()
        writer.addText("\n")

    writer.endElement()
    writer.endDocument()

if __name__ == "__main__":
    main()

#arch-tag: python script writing out a million elements

