#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8

##########################
#
# pyvideothumb
# simple script to create a big png file with video thumbs
# usage:
# python pyvideothum.py "video"
# python pyvideothum.py ""
#
#########################

########################
# Yangosoft
# http://code.google.com/p/pyvideothumb
# 
########################


import os
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import re
import datetime
import time


outputW = 1280
outputH = 1024
marginW = 15
marginH = 15
thumbW  = 250
outputTmpPath = "/tmp/tmpcreatethumb.jpg.tmp/"+str(time.time())

def show_usage():
  usage = """
python pyvideothumb.py video.avi
   > creates a thumbail named video.avi_thumb.jpg
python pyvideothumb.py "folder"
   > creates a thumbnail for each video found in "folder"
  """
  print usage


def main(argv=None):
    
  
  if argv is None:
    argv = sys.argv
  
  if (len(argv) == 1):
    show_usage()
    sys.exit(1)
  
  print argv
  
 
  if (os.path.isdir(argv[1])):
    processDir(argv[1])
  else:
    makeThumb(argv[1]) 
  
def getProps(file):
  line=""
  try:
    line = subprocess.check_output(["mplayer -vo null -ao null -frames 0 -identify " + file],shell=True)
  except:
    return [0,0,0]
  m = re.search('ID_VIDEO_HEIGHT.*.', line)
  h=0
  w=0
  l=0
  if(m):
    h=m.group(0).split('=')[1]
    m = re.search('ID_VIDEO_WIDTH.*.', line)
    w = m.group(0).split('=')[1]
    m = re.search('ID_LENGTH.*.', line)
    l = m.group(0).split('=')[1]
  return [ int(w),int(h),int(float(l))]
  
  
def makeThumb(file):
  
  
  
  props = getProps(file)
  
  if (props[0] == 0):
    return
  
  print str(file)
  
  thumbH  = (props[1] * thumbW) / props[0]
  columns = (outputW - marginW) / (thumbW + marginW) 
  #print "%d = %d ( %d + %d) + %d " % (outputW, columns, marginW, thumbW, marginW)
  rows    = (outputH - marginH) / (thumbH + marginH) 
  #print "%d = %d ( %d + %d) + %d " % (outputH, rows, marginH, thumbH, marginH)
  
  nMarginW = ( outputW - columns * thumbW ) / ( 1 +  columns )
  nMarginH = ( outputH - rows * thumbH ) / ( 1 +  rows )
  
  if(nMarginW < marginW):
    nMarginW = marginW
    
  if(nMarginH < marginH):
    nMarginH = marginH
  
  eachThumb = props[2] / (columns * rows)
  
  numCaptures = rows * columns
  
  if(eachThumb == 0):
    eachThumb = 1
    numCaptures = props[2]
  
  #print file + str(props) + " -> " + str(thumbW) + "x" + str(thumbH)
  #print "T: " + str(rows) + "x" + str(columns)
  #print "New margins " + str(nMarginW) + " " + str(nMarginH)
  #print str(numCaptures) + " captures, for each " + str(eachThumb)+" s"
  
  imOut = Image.new("RGB",(outputW,outputH))
  try:
    font    = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-R.ttf", 20)
  except:  
    font    = ImageFont.load_default()
  
  inst = 0
  
  for i in range(0,numCaptures):
    print "Processing " + str(i) + " of " + str(numCaptures-1)
    inst = i*eachThumb
    #print "mplayer -ss " + str(inst) +  " -nosound -vo jpeg -frames 1 '" + file + "' " + outputTmpPath
    try:
	subprocess.check_output(["mplayer -ss " + str(i*eachThumb) +  " -nosound -vo jpeg:outdir="+outputTmpPath+" -frames 1 '" + file + "' 2>/dev/null "],shell=True)
    except:
	pass
    im      = Image.open(outputTmpPath+"/00000001.jpg")
    im.thumbnail((thumbW,thumbH), Image.ANTIALIAS)
    
    draw    = ImageDraw.Draw(im)
    inst    = datetime.timedelta(seconds=inst)
    txtSize = draw.textsize(str(inst),font=font)

    draw.text(( thumbW-txtSize[0] -5 , thumbH - txtSize[1] - 5 ), str(inst), fill=(0xFF,0xFF,0), font=font)
    

    if (im):
      index = ((i / (columns) ),(i % (columns) ))
      #print str(i) + " index " + str(index) 
      #print "(%d,%d)" % ( nMarginW * index[1] + ( thumbW * index[1] ), nMarginH * index[0] + ( thumbH * index[0] )  )
      imOut.paste(im, ( nMarginW * (index[1] +1) + ( thumbW * index[1] ), nMarginH* (index[0]+1) + ( thumbH * index[0] )  ) )
      
  draw = ImageDraw.Draw(imOut)
  draw.text ((nMarginW,5),os.path.basename(file),font=font,fill=(0xFF,0xFF,0))  
  imOut.save(file+"_thumb.jpg")
  

  
  #mplayer -ss 10 -nosound -vo jpeg -frames 1 $i

def processDir(rootdir):
  global c
  global conn
  fileList = []
  fileSize = 0
  folderCount = 0
  tmpCache=[]
  print "DIR: " + rootdir
  for root, subFolders, files in os.walk(rootdir):
      #print "Processing: " + root
      folderCount += len(subFolders)
      for file in files:
	  f = os.path.join(root,file)
	  makeThumb(f)
	  fileList.append(f)

  
	  
if __name__ == "__main__":
  try:
    import psyco
    psyco.full()
  except ImportError:
    pass
  
  sys.exit(main())
