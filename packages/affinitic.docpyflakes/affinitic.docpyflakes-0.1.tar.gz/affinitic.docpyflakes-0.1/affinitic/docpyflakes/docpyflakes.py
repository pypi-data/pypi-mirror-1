# -*- coding: utf-8 -*-
"""
Doc Flakes (pyflakes for doctests)

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""

import popen2
import re
import shutil
import sys


def checkTextFile(filename):
    docFileR = open(filename, 'r')
    newLines = []
    originalLines = []
    isDocTest = False
    for line in docFileR.readlines():
        originalLines.append(line)
        if '>>>' not in line and '...' not in line: # handle comments
            newLines.append('#%s' % line)
        elif '>>>' in line:
            isDocTest = True
            match = re.match(re.compile('(\s+>>>\s)(.*)'), line)
            if match:
                newLines.append("%s\n" % match.groups()[1])
        elif '...' in line:
            match = re.match(re.compile('(\s+\.\.\.\s)(.*)'), line)
            if match:
                newLines.append("%s\n" % match.groups()[1])
    docFileR.close()

    if isDocTest == True: # it is a doctest !
        backupFilename = "%s.bak" % filename
        shutil.copy(filename, backupFilename)
        docFileW = open(filename, 'w')
        for newLine in newLines:
            if newLine.strip() != '#':
                docFileW.write('%s' % newLine)
            else:
                docFileW.write('\n')

        docFileW.close()
        pop = popen2.Popen3('/usr/bin/pyflakes %s' % filename,
                            capturestderr=True)
        pop.wait()
        sys.stdout.writelines(pop.fromchild.readlines())
        shutil.copy(backupFilename, filename)


def main():
    checkTextFile(sys.argv[1])

if __name__ == '__main__':
    main()
