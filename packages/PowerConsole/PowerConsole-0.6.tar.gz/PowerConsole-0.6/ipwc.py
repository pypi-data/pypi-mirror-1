#!/usr/bin/python
#
#   PROGRAM:     PowerConsole
#   MODULE:      ipwc.py
#   DESCRIPTION: PowerConsole Main script - CLI console version
#
#  The contents of this file are subject to the Initial
#  Developer's Public License Version 1.0 (the "License");
#  you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.firebirdsql.org/index.php?op=doc&id=idpl
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#
#  Copyright (c) 2007-2009 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

"""ipwc is bare bone CLI version of PowerConsole."""

from pwc.interpreter import interact
from pwc.release import *
import sys

def main():
    """The main function for the CLI PowerConsole program."""
    
    hdr = '%s v%s [CLI version]\nPython %s on %s\n\n%s\n'
    interact(hdr % (name,version,sys.version,sys.platform,
              'Type "help" for more information.'))

if __name__ == '__main__':
    main()
