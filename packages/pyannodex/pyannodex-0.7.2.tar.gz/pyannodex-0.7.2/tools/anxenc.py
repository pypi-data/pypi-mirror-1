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
                          description = "Encapsulate data into annodexed media.")
    parser.add_option("-t", "--type",
                      action="store", type="string", dest="content_type",
                      default=None,
                      help="Extract annotation as a valid CMML file (default)")
    parser.add_option("-o", "--output",
                      action="store", type="string", dest="output", default=None,
                      help="Specify output filename (default is stdout).")
    (options, args) = parser.parse_args()

    # Get input filename
    if len(args) != 1:
        parser.print_help()
        return

    # Setup output file
    anx = annodex.Writer(options.output)

    # Generate anx object
    anx.import_file(args[0], mime_type=options.content_type)

    # Write output
    anx.write()

if __name__ == "__main__":
    main()
