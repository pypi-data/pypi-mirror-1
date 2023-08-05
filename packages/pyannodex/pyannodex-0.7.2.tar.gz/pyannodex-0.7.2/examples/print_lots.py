"""
This is the python version of libannodex/src/examples/print-lots.c

Copyright (c) 2004 Ben Leslie (benno@benno.id.au)

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of Ben Leslie nor the names of his
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

import annodex

class my_data:
    def __init__(self, filename):
        self.filename = filename
        self.done = 0
        self.interesting_serialno = 0
        self.interesting_raw_packets = 0

def read_stream(anx, timebase, utc, happy):
    print "Welcome to %s! The timebase is %f" % (happy.filename, timebase)

def read_track(anx, serialno, track_id, content_type, granule_rate_n, granule_rate_d,
               nr_head_packets, happy):
    if content_type == "text/x-cmml":
        return

    print "Our first track has content-type %s and granule rate %ld/%ld." % (content_type, granule_rate_n, granule_rate_d)
    print "We will remember it by its serial number %ld and mark it with crosses." % (serialno)
    happy.interesting_serialno = serialno
    anx.set_read_track_callback(None)

def read_raw(anx, buff, serialno, granulepos, happy):
    if happy.done:
        sys.stdout.write('!')
    elif serialno == happy.interesting_serialno:
        happy.interesting_raw_packets += 1
        sys.stdout.write('+')
    else:
        sys.stdout.write(".")

def read_clip3(anx, clip, happy):
    if not clip.anchor:
        href = "(null)"
    else:
        href = clip.anchor["href"]
    print "\nAnd the third clip links to %s" % href
    happy.done = 1
    print "This completes our whirlwind tour of the first three clips!"

def read_clip2(anx, clip, happy):
    if not clip.anchor:
        href = "(null)"
    else:
        href = clip.anchor["href"]
    print "\nThe second clip links to %s" % href
    anx.set_read_clip_callback(read_clip3, happy)

def read_clip1(anx, clip, happy):
    if not clip.anchor:
        href = "(null)"
    else:
        href = clip.anchor["href"]
    print "\nThe first clip links to %s" % href
    anx.set_read_clip_callback(read_clip2, happy)

def main(argv):
    if len(argv) != 2:
        print "Usage: python print_title_file.py file.anx"
        return
    
    me = my_data(argv[1])

    anx = annodex.Anx(me.filename, "r")
    
    anx.set_read_stream_callback (read_stream, me)
    anx.set_read_track_callback (read_track, me)
    anx.set_read_raw_callback (read_raw, me)
    anx.set_read_clip_callback (read_clip1, me)    

    while 1:
        x = anx.read(1024)
        if x <= 0:
            break
        if me.done:
            break

    print "%d packets from the first track (serialno %ld) were received" % \
          (me.interesting_raw_packets, me.interesting_serialno)
    print "before the third clip."

if __name__ == "__main__":
    import sys
    main(sys.argv)
