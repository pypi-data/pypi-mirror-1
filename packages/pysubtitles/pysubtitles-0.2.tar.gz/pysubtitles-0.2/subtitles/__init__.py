# -*- coding: utf-8 -*-
# vi:si:et:sw=2:sts=2:ts=2
# GPL 2008 j@oil21.org
import re
import os
from os.path import abspath, join, dirname
import shutil
import time

import chardet


class Subtitle(dict):
  def __unicode__(self):
    txt = u''
    for k in sorted([int(k) for k in self]):
      txt += u"%s\n" % self["%s" % k]['text']
    return txt.strip()

  def loadSrtFile(self, fname):
    f = open(fname)
    encoding = _detectEncoding(f)
    data = f.read()
    f.close()
    try:
      udata = unicode(data, encoding)
    except:
      try:
        udata = unicode(data, 'latin-1')
      except:
        print "failed to detect encoding, giving up"
        udate = u''
    if udata.startswith(u'\ufeff'): 
      udata = udata[1:]
    self.loadSrt(udata)

  def loadSrt(self, srt):
    _srt = re.sub(r'\r\n|\r|\n', '\n', srt)
    subtitles = _srt.strip().split('\n\n')
    for subtitle in subtitles:
      if subtitle.strip():
        subtitle = subtitle.lstrip().split('\n')
        if len(subtitle) >= 2:
          io = subtitle[1].split('-->')
          io[0] = io[0].strip().split(' ')[0]
          io[0] = re.sub('(\d{2}).(\d{2}).(\d{2}).(\d{3})', '\\1:\\2:\\3,\\4', io[0])
          io[1] = io[1].strip().split(' ')[0]
          io[1] = re.sub('(\d{2}).(\d{2}).(\d{2}).(\d{3})', '\\1:\\2:\\3,\\4', io[1])
          sub_id ="%s" % int(subtitle[0])
          self[sub_id] = {
            'in': io[0],
            'out': io[1],
            'text': u'\n'.join(subtitle[2:]),
          }

  def toSrt(self):
    srt = u""
    for k in sorted([int(k) for k in self]):
      k = "%s" % k
      srt += u"%s\r\n%s --> %s\r\n%s\r\n\r\n" % (
        k, 
        self[k]['in'],
        self[k]['out'],
        self[k]['text'])
    return srt

  def shift(self, msec):
    "shift subtitles by msec"
    for k in sorted([int(k) for k in self]):
      k = "%s" % k
      self[k]['in'] = shiftTime(msec, self[k]['in'])
      self[k]['out'] = shiftTime(msec, self[k]['out'])

  def merge(self, otherSubtitle, offset):
    next = max([int(k) for k in self]) + 1
    for _k in sorted(otherSubtitle):
      self["%s" % next] = {
            'in': shiftTime(offset, otherSubtitle[_k]['in']),
            'out': shiftTime(offset, otherSubtitle[_k]['out']),
            'text': otherSubtitle[_k]['text'],
      }
      next += 1

  def split(self, offset):
    s0 = Subtitle()
    s1 = Subtitle()
    next = 0
    for _k in sorted(self):
      if time2ms(self[_k]['in']) < offset:
        s0[_k] = self[_k]
      else:
        s1["%s" % next] = {
            'in': shiftTime(-offset, self[_k]['in']),
            'out': shiftTime(-offset, self[_k]['out']),
            'text': self[_k]['text'],
        }
        next += 1
    return s0, s1

def test_subtitle():
  s = Subtitle()
  srt = u'''0
00:00:00,000 --> 00:00:00,000
Interview with Fred von Lohmann

1
00:00:05,800 --> 00:00:10,120
The last 100 years have been
a story of resistance on

2
00:00:10,360 --> 00:00:14,400
on the part of incumbents,
largely entertainment companies,'''
  s.loadSrt(srt)
  assert len(s) == 3

  assert s['0']['in'] == '00:00:00,000'
  assert s['1']['out'] == '00:00:10,120'
  assert s['2']['in'] == '00:00:10,360'

  s.shift(1001)
  assert s['2']['in'] == '00:00:11,361'
  s.shift(-1000)
  assert s['1']['out'] == '00:00:10,121'

def ms2time(ms):
  '''
  >>> ms2time(44592123)
  '12:23:12,123'
  '''
  it = int(ms / 1000)
  ms = ms - it*1000
  ss = it % 60
  mm = ((it-ss)/60) % 60
  hh = ((it-(mm*60)-ss)/3600) % 60
  return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms)

def time2ms(timeString):
  '''
  >>> time2ms('12:23:12,123')
  44592123
  '''
  ms = 0.0
  p = timeString.replace(',', '.').split(':')
  for i in range(len(p)):
    ms = ms * 60 + float(p[i])
  return int(ms * 1000)

def shiftTime(offset, time_string):
  ''' return time shifted by offset milliseconds
  
  >>> shiftTime(1000, '00:00:10,360')
  '00:00:11,360'
  '''
  return ms2time(time2ms(time_string) + offset)

def _detectEncoding(fp):
  bomDict={ # bytepattern : name              
            (0x00, 0x00, 0xFE, 0xFF) : "utf_32_be",        
            (0xFF, 0xFE, 0x00, 0x00) : "utf_32_le",
            (0xFE, 0xFF, None, None) : "utf_16_be", 
            (0xFF, 0xFE, None, None) : "utf_16_le", 
            (0xEF, 0xBB, 0xBF, None) : "utf_8",
          }

  # go to beginning of file and get the first 4 bytes
  oldFP = fp.tell()
  fp.seek(0)
  (byte1, byte2, byte3, byte4) = tuple(map(ord, fp.read(4)))

  # try bom detection using 4 bytes, 3 bytes, or 2 bytes
  bomDetection = bomDict.get((byte1, byte2, byte3, byte4))
  if not bomDetection :
      bomDetection = bomDict.get((byte1, byte2, byte3, None))
      if not bomDetection :
          bomDetection = bomDict.get((byte1, byte2, None, None))

  ## if BOM detected, we're done :-)
  fp.seek(oldFP)
  if bomDetection :
      return bomDetection

  encoding = 'latin-1'
  #more character detecting magick using http://chardet.feedparser.org/
  fp.seek(0)
  rawdata = fp.read()
  encoding = chardet.detect(rawdata)['encoding']
  fp.seek(oldFP)
  return encoding

