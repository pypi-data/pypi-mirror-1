#!/usr/bin/env python2.0
# $Id: buildmetrics.py,v 1.1 2002/01/22 02:51:42 clee Exp $
# build a files for piddle/sping PS that store the font metric info




import sys, string
print sys.version

from fontTools.agl import UV2AGL #, AGL2UV
import fontTools.afmLib

import pidPS
import fontinfo

M_aglName = UV2AGL[ord('M')]


from pyart._fontmap import font2file  # 

# pid fontname ---| font2file >  --> fontfilename.pfb --[strip add afm] -> afmfilename

# read AFM file for a font
def font2afm(adobeFontName):
    pfb = font2file[adobeFontName]
    afm = pfb[:-3] + "afm"  # works here
    return afm

def getAFM(adobeFontName):
    afmFileName = font2afm(adobeFontName) 
    return fontTools.afmLib.AFM(path=afmFileName)



def latin1FontWidth_DictCode(afm, pid_font_name):
    """Returns python code for a dictionary mapping a PID font name to an array of
    glyph widths as described in the afm class"""
    # if using python 2.0 w/ unicode could use other options

    dictCodeStr = []
    widthArraySubStr = []
    
    dictCodeStr.append( """ '%s': [ """ % string.lower(pid_font_name) )
    
    for latin1 in range(256):

        # take advantage of the fact that latin-1 encoding matches
        # unicode for first 256 characters
        
        if UV2AGL.has_key(latin1):
            name = UV2AGL[ latin1]  
        else:
            name = ".notdef"
            #print "doesn't have latin1 code %d so giving it name %s" % (latin1, name)

        if afm._chars.has_key(name):
            metric = afm._chars[name]
        else:  
            try:
                metric = afm[".notdef"]
            except KeyError:
                try:
                    metric = afm[M_aglName] # which is 'M' for now
                except KeyError:
                    metric = (-1, 250, (0,0,0,0) )  # a fallback

        stdchr, width, bbox = metric
        widthArraySubStr.append("%s" % width)

    dictCodeStr.append(string.join(widthArraySubStr, ", "))
    dictCodeStr.append("]") # close array
    return string.join(dictCodeStr, " ")

def generateCache():
    code = []
    for fontname in fontinfo.StandardRomanFonts :
        print "doing font %s" % fontname
        afm = getAFM(fontname)


        code.append( latin1FontWidth_DictCode(afm, string.lower(fontname) ) )


    fp = open("latin1MetricsCache.py", "w")
    fp.write("FontWidths = {  \n" )
    code = string.join(code, ",\n")
    fp.write(code)
    fp.write("} \n")
    fp.close()


if __name__ == '__main__':
    print "Generating latin1MetricsCache.py"
    generateCache()


