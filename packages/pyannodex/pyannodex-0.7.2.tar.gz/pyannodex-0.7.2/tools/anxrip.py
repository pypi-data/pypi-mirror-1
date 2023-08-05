#!/usr/bin/env python
"""
This is the python version of libannodex/src/tools/anxrip.c

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

def main():
    # Generate option parser
    parser = OptionParser(usage = "%prog [options] file",
                          description = "Extract (rip) data from annodex media.")
    parser.add_option("-c", "--cmml",
                      action="store_true", dest="print_cmml",
                      default=True,
                      help="Extract annotation as a valid CMML file (default)")
    parser.add_option("--head",
                      action="store_true", dest="print_head",
                      default=False,
                      help="Extract only the CMML head element")
    parser.add_option("-o", "--output",
                      action="store", type="string", dest="output",
                      help="Specify output filename (default is stdout).")
    (options, args) = parser.parse_args()

    # Get input filename
    if len(args) != 1:
        parser.print_help()
        return
    filename = args[0]

    # Setup output file
    output = sys.stdout
    if options.output:
        output = open(options.output, "w")

    # Generate anx object
    anx = annodex.Reader(filename)

    # Now do the actual work
    if options.print_cmml:
        if options.print_head:
            print >> output, anx.head.get_cmml()
        else:
            print >> output, anx.get_cmml()

if __name__ == "__main__":
    main()
