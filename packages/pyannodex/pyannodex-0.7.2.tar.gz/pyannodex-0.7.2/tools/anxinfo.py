#!/usr/bin/env python
"""
This is the python version of libannodex/src/tools/anxinfo.c

Copyright (c) 2004 Ben Leslie (benno@benno.id.au)

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

- Neither the name of CSIRO Australia nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE ORGANISATION OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from optparse import OptionParser
import annodex, sys

nr_clips = 0
raw_size = 0


def str_time_npt(seconds):
    if seconds < 0.0:
        sign = "-"
    else:
        sign = ""

    if seconds < 0.0:
        seconds = -seconds

    hrs = int(seconds/3600.0)
    min = int((seconds - (hrs * 3600.0)) / 60.0)
    sec = seconds - (hrs * 3600.0) - (min * 60.0)
    return "%s%02d:%02d:%06.3f" % (sign, hrs, min, sec)

def read_clip(anx, clip):
    global nr_clips
    nr_clips += 1

def read_raw(anx, data, serialno, granulepos):
    global raw_size
    raw_size += len(data)

def main():
    # Generate option parser
    parser = OptionParser(usage = "%prog [options] file",
                          description = "Display information about annodexed media.")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      default=False,
                      help="Display verbose information about file")
    (options, args) = parser.parse_args()

    # Get input filename
    if len(args) != 1:
        parser.print_help()
        return
    filename = args[0]

    # Generate anx object
    anx = annodex.Anx(filename, "r")

    # Now do the actual work
    if options.verbose:
        print "# anxinfo " + annodex.__version__ + "\t\t\thttp://www.annodex.net/\n";
        print "* Filename: %s\n" % filename;
        print "%-20s%-10s  %12s %7s %-20s" % \
              ("# id", "Serial", "Granule rate", "+Hdrs", "Content-Type")

    anx.set_read_clip_callback(read_clip)
    anx.set_read_raw_callback(read_raw)

    while 1:
        x = anx.read(1024)
        if x <= 0:
            break

    for track in anx.get_track_list():
        if track["id"] is None:
            track_id = "-- unidentified --"
        else:
            track_id = track["id"]
        gran_rate = "%d/%d" % (track["granule_rate_n"], track["granule_rate_d"])
        print "%-20s%-10s  %12s %7s %-20s" % \
              (track_id, track["serialno"], gran_rate, track["nr_header_packets"], track["content_type"])
        print "\tbasegranule %d\tpreroll %d\tgranuleshift %d" % (track["basegranule"],
                                                                 track["preroll"],
                                                                 track["granuleshift"])
        #anx_track_get_granuleshift (anx, s->serialno));

    if options.verbose:
        print "\n*CMML:\t\t\t%d clips" % nr_clips;
        print "*Content-Length:\t%ld bytes" % raw_size;
        print "*Presentation time:\t", str_time_npt(anx.get_presentation_time())
        print "*Basetime:\t\t", str_time_npt(anx.get_basetime())
        print "*Duration:\t\t", str_time_npt(anx.get_duration())
        bitrate = anx.get_bitrate (anx);
        if bitrate > 0.0:
            print "*Bitrate-Average:\t%.0f bps" % bitrate;

if __name__ == "__main__":
    main()
