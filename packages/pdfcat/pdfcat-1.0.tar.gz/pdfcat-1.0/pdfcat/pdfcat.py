# -*- coding: utf-8 -*-
#
# File: pdfcat.pdfcat
#
# Copyright (c) 2007 atReal
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
$Id$
"""

__author__ = """Jean-Nicolas Bès <contact@atreal.net>"""
__docformat__ = 'plaintext'
__licence__ = 'GPL'

import os
import sys
import shutil
import tempfile
import StringIO
from os.path import isfile, abspath, join

class PdfJoiner:
    pdflatex="/usr/bin/pdflatex"
    
    paper="a4paper"        ## alternatives are other LaTeX paper sizes 
    orient="portrait"
    fitpaper="true"        ## output page size matches input
    turn="true"            ## landscape pages are landscape-oriented
    noautoscale="false"    ## scale logical pages to fit  
    offset="0 0"           ## output centred on physical page
    trim="0 0 0 0"         ## don't trim the logical pages
    tidy="true"            ## delete all temporary files immediately
    
    
    prologfmt = ("\\documentclass[%s,%s]{article}\n"
        "\\usepackage{pdfpages}\n"
        "\\begin{document}\n")
    
    pdfitemfmt = """\\includepdf[pages=-,fitpaper=%s,trim=%s,offset=%s,turn=%s,noautoscale=%s]{%s}\n"""
    
    epilog = """\\end{document}\n"""
    
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if not key in ('paper', 'orient', 'fitpaper', 'turn', 'noautoscale', 'offset', 'trim', 'tidy'):
                continue
            setattr(self, key, val)

    def makeInputAvail(self, tmpdirpath, inputs):
        tmpinputs=[]
        toclean=[]
        for inp in inputs:
            if isinstance(inp, (str, unicode)):
                if len(inp)<2000 and isfile(inp):
                    filename = tempfile.mktemp(dir=tmpdirpath, suffix=".pdf")
                    os.symlink(abspath(inp), filename)
                else:
                    tmpfile, filename = tempfile.mkstemp(text=False, dir=tmpdirpath, suffix=".pdf")
                    os.write(tmpfile, inp)
                    os.close(tmpfile)
            elif isinstance(inp, file) and isfile(abspath(inp.name)):
                filename = tempfile.mktemp(dir=tmpdirpath, suffix=".pdf")
                os.symlink(abspath(inp.name), filename)
            elif hasattr(inp, '__iter__'):
                tmpfile, filename = tempfile.mkstemp(text=False, dir=tmpdirpath, suffix=".pdf")
                for line in inp:
                    os.write(tmpfile, line)
                os.close(tmpfile)
                filename = abspath(filename)
            else:
                print "WTF?", repr(inp)
                continue
            #filename.replace(".", "\.")
            tmpinputs.append(filename)
        return tmpinputs
    
    def processOutput(self, outfilepath, want):
        tmpoutput = file(outfilepath)
        if want is str:
            output = tmpoutput.read()
        elif want is StringIO.StringIO:
            output = StringIO.StringIO(tmpoutput.read())
        elif isinstance(want, str):
            want = file(want, 'w')
        if isinstance(want, (file, StringIO.StringIO)):
            want.write(tmpoutput.read())
            output = want
        return output
    
    def joinpdfs(self, inputs, want=str, **kwargs):
        print "INPUT", inputs
        print "WANTR", repr(want)
        #add kwargs
        self.__init__(**kwargs)
        
        #make temporary working dir
        tmpdirpath = tempfile.mkdtemp()
        #print tmpdirpath
        tmptexfile, tmptexname = tempfile.mkstemp(text=False, dir=tmpdirpath)
        
        #fill tmpinputs with (maybe temporary) input files as <open file>
        tmpinputs = self.makeInputAvail(tmpdirpath, inputs)
        
        #build tex file
        #print self.prologfmt % (self.paper, self.orient)
        os.write(tmptexfile, self.prologfmt % (self.paper, self.orient))
        
        for inp in tmpinputs:
            pdfitem = self.pdfitemfmt % (self.fitpaper,
                                         self.trim,
                                         self.offset,
                                         self.turn,
                                         self.noautoscale,
                                         inp)
            #print pdfitem
            os.write(tmptexfile, pdfitem)
        
        #print self.epilog
        os.write(tmptexfile, self.epilog)
        
        #print "-"*60
        
        #call pdf latex
        os.system("cd %s && pdflatex -halt-on-error %s >/dev/null" % (tmpdirpath,tmptexname))
        print os.getcwd()
        outfilepath = join(tmpdirpath, tmptexname+".pdf")
        
        if not isfile(outfilepath):
            print "Une erreur s'est produite"
            return
        
        #make the output suit the user needs
        output = self.processOutput(outfilepath, want)
        
        #do the necessary cleanup
        shutil.rmtree(tmpdirpath)
        
        return output

if __name__=="__main__":
    if len(sys.argv) < 3:
        raise SystemExit, "Au moins 2 arguments!!!"
    pj = PdfJoiner()
    print "INPUT", sys.argv[1:-1], "OUTPUT", sys.argv[-1]
    pj.joinpdfs(sys.argv[1:-1], want=sys.argv[-1])
