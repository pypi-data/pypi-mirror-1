#!/usr/bin/env python
"""Rewrite VEVENT's DTSTART and DTEND if they're midnight to midnight"""

from optparse import OptionParser
import icalendar, base, datetime
import os
import codecs
import PyICU

pst = PyICU.ICUtzinfo.getInstance('US/Pacific')

def changeVeventTimes(vevent):
    dtstart = vevent.getChildValue('dtstart')
    dtend   = vevent.getChildValue('dtend')
    if isinstance(dtstart, datetime.datetime):
        if dtstart.tzinfo is None:
            vevent.dtstart.value = dtstart.replace(tzinfo=pst)
        if dtend is not None and dtend.tzinfo is None:
            vevent.dtend.value   = dtend.replace(tzinfo=pst)

def main():
    options, args = getOptions()
    if args:
        in_filename, out_filename = args
        cal = base.readOne(file(in_filename))
        for vevent in cal.vevent_list:
            changeVeventTimes(vevent)
        out_file = codecs.open(out_filename, "w", "utf-8")
        cal.serialize(out_file)
        out_file.close()


version = "0.1"

def getOptions():
    ##### Configuration options #####

    usage = "usage: %prog [options] in_file out_file"
    parser = OptionParser(usage=usage, version=version)
    parser.set_description("convert midnight events to all")
    
    (cmdline_options, args) = parser.parse_args()
    if len(args) < 2:
        print "error: too few arguments given"
        print
        print parser.format_help()
        return False, False

    return cmdline_options, args

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Aborted"
