##########################################################################
# haufe.eggserver
# (C) 2008, Haufe Mediengruppe Freiburg, ZOPYX Ltd. & Co. KG
# Written by Andreas Jung
# Published under the Zope Public License V 2.1
##########################################################################

import sys
import re
from zipfile import ZipFile
from util import *

line_reg = re.compile(r'^([\w-]*): (.*)')

def parse_metadata(egg_filename):
    """ Parse EGG-INFO/PKG-INFO """

    ZF = ZipFile(egg_filename, 'r')
    pkg_info = ZF.read('EGG-INFO/PKG-INFO')
    ZF.close()

    lines = pkg_info.split('\n')
    d = dict()
    old_ident = ident = old_value = value = ''

    num_lines = len(lines)
    for i in range(num_lines):
        line = lines[i].rstrip()
        mo = line_reg.match(line)

        if mo:
            ident = mo.group(1)
            if old_ident and old_ident != ident and old_value:
                d[old_ident] = toUnicode(value)
                value = ''
            value += mo.group(2)

            if i < num_lines-1:
                if line_reg.match(lines[i+1]):
                    d[ident] = toUnicode(value)
                    value = ''
        else:
            value += '\n' + line
        old_ident = ident
        old_value = value

    d[ident] = toUnicode(value)
    return d

if __name__ == '__main__':
    for k,v in parse_metadata(sys.argv[1]).items():
        print '-'*80
        print k,v
