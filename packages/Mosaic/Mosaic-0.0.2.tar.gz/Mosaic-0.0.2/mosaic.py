#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Mosaic poster composer

For a given image tries to create the same image from small images found in
the given files/directories.

Needs PIL (Python Image Library) for image manipulation.

SYNOPSYS
    Each donor picture is resized to <precision>x<precision> size 
  (using a "fit" method - resize and crop for the best fit), and its
  pixel matrix stored in data.db with its file path, so can be reused for
  another run (even for another original picture).
    Then the original picture is resized to <width>/<num>*<prec> width and
  height, and its matrix is used to find the best picture for each place.
  The comparation uses a simple least square method.
    Every picture is used once, and if there is not enough, then they are
  used again, but there will be "equality" among picture usage: no picture
  is used more than the others.
    As you may found out, the matching order can be crucious, so the little
  matching rectangles' order is randomized (maybe another approach would be
  better: from the center in spiral to the outer - but I didn't have time
  to work out this algorithm yet).

    The number of threads running parallel can fasten the process seriously.
  But keep in mind, that every thread makes a small picture from the donor,
  so memory consumption can crawl up, and swapping kills the speed.
    Another limiting factor is the context switching needed between threads,
  so you should try out several -tN scenarios to find the best for your
  machine.

  Usage example: 
  
  mosaic.py -p5 -n40 -t13 --blend 30 --blend 40 xx.jpg /path/to/my/pics
    will make a mosaic from the pictures found in /path/to/my/pics for
    the picture xx.jpg, as big as the original one, 40 pictures in a row,
    40 rows (total 1600 picture), precision 5 (the default),
    and beside the untouched "raw" result, itt will make two compositions,
    having the original picture blended in for 30%, 40% respectivly.
      No output is specified, so the results will be 
    xx-mosaic-5-40-<width>x<height>-0.jpg
    xx-mosaic-5-40-<width>x<height>-30.jpg
    xx-mosaic-5-40-<width>x<height>-40.jpg

HISTORY

  0.0.2: added a --blend option for blending with the original picture. 
         It accepts a number as percentage for the original 
         (0 is none - the default, a good deal is about 30-40).
           Also some documentation is written

  0.0.1: initial version
'''

__author__ = 'Tamás Gulácsi'
__version__ = '0.0.2'

import os, sys, shelve, threading, operator, optparse, random, sha
from glob import glob
from time import time, sleep
from PIL import Image, ImageOps

#get rid of that pesky RuntimeWarning for os.tempnam()
import warnings
warnings.filterwarnings('ignore', message=r'.*\btempnam\b.*')
tmpdir = os.tempnam()

def get_hash(inp):
  '''Returns the hash of the given file (by filename or file object)'''
  if isinstance(inp, basestring): fh = open(inp, 'rb')
  else: fh = inp
  s = sha.new()
  while 1:
    buf = fh.read(8192)
    if buf is None or len(buf) == 0: break
    s.update(buf)
  return s.hexdigest()

def get_image_files(files, exts=['.jpg']):
  '''Returns the image files found in the files and directories

  Only names matching the given ext are found'''
  def ext_ok(fn):
    for ext in exts: 
      if fn.endswith(ext): return True
    return False

  res = []
  for name in files:
    if os.path.isdir(name):
      for root, dirs, files in os.walk(os.path.abspath(name)):
        res.extend(os.path.join(root, fn) for fn in files 
                   if ext_ok(fn))
    else: 
      if os.path.isfile(name) and ext_ok(name): res.append(name)
  return res

def unflat_matrix(mtx, row_len):
  '''Unflattens the matrix - generator

  Makes rows in row_len length -- e.g. mtx=[1,2,3,4,5,6], row_len=2 
    -> [[1,2], [3,4], [5,6]]
  '''
  assert row_len > 0 and  len(mtx) > 0 and len(mtx) % row_len == 0
  for i in xrange(0, len(mtx)/row_len):
    yield tuple(mtx[i*row_len:(i+1)*row_len])

def get_img_matrix(img):
  '''Returns the (unflattened) matrix of an image's pixel data'''
  return tuple(unflat_matrix(tuple(img.getdata()), img.size[0]))

def image_matrix(fn, size):
  '''Returns the matrix of an image (given by filename) resized to the 
  given size'''
  im1 = Image.open(fn)
  im1.draft('RGB', size)
  im2 = ImageOps.fit(im1, size, Image.ANTIALIAS)
  #im2 = im1.resize(size, Image.ANTIALIAS)
  return get_img_matrix(im2)

def diff(vec1, vec2):
  '''Computes the difference of two vectors 

  Uses Least Square method'''
  assert len(vec1) == len(vec2)
  return sum((vec1[i]-vec2[i])**2 for i in xrange(0, len(vec1)))

def mtx_diff(mtx1, mtx2):
  '''Computes the difference of two matrices

  Least Square method for mtx1-mtx2'''
  assert len(mtx1) == len(mtx2)
  def sqr(a): return a**2
  return sum(map(sqr, (sum(diff(mtx1[i][j], mtx2[i][j])**2 for j in xrange(0, len(mtx1[i]))) for i in xrange(0, len(mtx1)))))

def get_matrices(db_fn, files, precision, exts=['.jpg']):
  '''Returns the matrices with given precision from files, cached in the 
  db_fn'''
  size = (precision, precision)
  db = shelve.open(db_fn)
  matrices = set()
  hashes = set()
  for fn in get_image_files(files, exts):
    if (not db.has_key(fn) or db[fn] is None 
        or not isinstance(db[fn], dict) or not db[fn].has_key(size)
        or not db[fn].has_key('hash')
        or not isinstance(db[fn][size], tuple)):
      d = {size: image_matrix(fn, size), 'hash': get_hash(fn)}
      if not db.has_key(fn) or not isinstance(db[fn], dict): 
        db[fn] = d.copy()
      else: 
        c = dict(db[fn])
        c.update(d)
        db[fn] = c
      # print db[fn]
      db.sync()
    #
    htup = (db[fn][size], db[fn]['hash']) 
    if htup not in hashes:
      hashes.add(htup)
      matrices.add((db[fn][size], fn))
  db.sync()
  db.close()
  return matrices

def do_one(reszlet, matrices, pos, egy, tgt, lock):
  '''Finds the best match for one small picture'''
  # print lock.locked()
  lock.acquire()
  #print 'len(matrices):', len(matrices)
  best = min(((rank, mtx_diff(reszlet, matrix)), (matrix, fn, rank))
    for matrix, fn, rank in matrices)[-1]
  matrices.remove(best)
  matrices.add((best[0], best[1], best[2]+1))
  lock.release()
  kicsi = Image.open(best[1])
  kicsi = ImageOps.fit(kicsi, egy, Image.ANTIALIAS)
  if isinstance(tgt, list): tgt.append((kicsi, pos))
  elif isinstance(tgt, dict) or hasattr(tgt, 'sync'): 
    nev = 'tmp-%d-%d.jpg' % pos
    temp_save(kicsi, nev)
    tgt[pos] = nev
    if hasattr(tgt, 'sync'): tgt.sync()
  #else: img.paste(kicsi, pos)
  # print pos, best
  del kicsi

def clean_pool(pool, join=False):
  '''Cleans the thread pool from the stopped threads'''
  for th in [x for x in pool if not x.isAlive()]: 
    pool.remove(th)
    if join: th.join()
  return pool

def run(running, pool, parallel=2):
  '''Runs the threads given in the pool, at most parallel in a given time'''
  # clean_pool(running)
  x = 0
  while len(running)+len(pool) > 0:
    clean_pool(running, join=True)
    sys.stdout.write('\b'*6 + '%06d' % (len(running)+len(pool)))

    n = min(max(parallel-len(running), 0), len(pool))
    # print n
    if n > 0:
      x = 0
      for th in pool[0:n]: th.start()
      running.extend(pool[0:n])
      del pool[0:n]
    else:
      x += 1
      if x > 100: break
    # print running, pool
    sleep(1)

def temp_save(img, name):
  '''saves the image in tmpdir on the given name'''
  global tmpdir
  if not os.path.exists(tmpdir): os.mkdir(tmpdir)
  fn = os.path.join(tmpdir, name)
  img.save(fn)
  assert os.path.exists(fn)

def temp_read(name):
  '''returns the image saved as name in tmpdir'''
  global tmpdir
  if not name.startswith(tmpdir): name = os.path.join(tmpdir, name)
  return Image.open(name)

def temp_del(name=None):
  '''Deletes the temporary image(s)'''
  global tmpdir
  if name is None:
    for fn in os.listdir(tmpdir): 
      try: os.unlink(os.path.join(tmpdir, fn))
      except OSError: pass
    if os.path.exists(tmpdir): 
      try: os.rmdir(tmpdir)
      except OSError: pass
  else: 
    if not name.startswith(tmpdir): name = os.path.join(tmpdir, name)
    if os.path.exists(name): 
      try: os.unlink(name)
      except OSError: pass

def main(base_fn, files, imgnum=3, precision=3, threadnum=3, 
         **opts):
  '''Main function

  Gathers the files, fills the database with the patterns (small matrices),
  Creates a thread for each small picture (imgnum**2), and then runs the 
  threads, threadnum at most in parallel.
  Finally combines the computed small images to the result (and deletes the 
  temporary files)
  '''
  matrices = set(tuple(list(tup) + [0]) 
    for tup in get_matrices(opts['workdb'], files, precision, 
                            exts=opts['exts']))

  base_img = Image.open(base_fn)
  if opts.has_key('dest_size'):
    print opts['dest_size']
    base_img = ImageOps.fit(base_img, opts['dest_size'])
  tgt_size = ((base_img.size[0]/imgnum)*imgnum, 
      (base_img.size[1]/imgnum)*imgnum)
  base_blend = base_img.resize(tgt_size, Image.ANTIALIAS)
  temp_save(base_blend, 'base_blend.jpg')
  print base_blend.size, tgt_size
  del base_blend
  base_img = base_img.resize((imgnum*precision, imgnum*precision), 
    Image.ANTIALIAS)
  base_img = ImageOps.autocontrast(base_img, 3)
  temp_save(base_img, 'base.jpg')
  base_mtx = get_img_matrix(base_img)
  del base_img

  egy = (tgt_size[0]/imgnum, tgt_size[1]/imgnum)
  # print tgt_size, egy
  pool = []
  running = []
  # if os.path.exists('temp'): os.unlink('temp')
  # result = shelve.open('temp')
  result = {}
  lock = threading.Lock()
  t = time()
  for r in xrange(0, imgnum):
    for c in xrange(0, imgnum):
      reszlet = [base_mtx[r*precision+i][c*precision:(c+1)*precision] 
        for i in xrange(0, precision)]
      pos = (c*egy[0], r*egy[1])
      # do_one(reszlet, matrices, pos, egy, result, lock)
      pool.append(threading.Thread(target=do_one, 
        args=(reszlet, matrices, pos, egy, result, lock)))
  #
  print 'Starting %d threads...' % threadnum
  rnd = random.SystemRandom()
  rnd.shuffle(pool)
  run(running, pool, threadnum)
  #print running, pool, result
  img = Image.new('RGB', tgt_size)
  num = len(result)
  i = 0
  print '\nComposition starts...'
  if isinstance(result, dict):
    for pos, kicsi in result.iteritems():
      # print pos, kicsi
      i += 1
      sys.stdout.write('\b'*6 + '%02.03f%%' % (float(i)/num))
      if isinstance(kicsi, basestring):
        nev = kicsi
        kicsi = temp_read(nev)
      img.paste(kicsi, pos)
      # img.save(out_fn)
      #if locals().has_key('nev'): temp_del(nev)
  # else: sys.exit(1)
  print '\n%.03fs' % (time()-t)
  stats = {}
  for mtx, fn, rank in matrices:
    if not stats.has_key(rank): stats[rank] = 1
    else: stats[rank] += 1
  for k in sorted(stats.iterkeys()):
    print '%d images used for %d times' % (stats[k], k)
  return img

if __name__ == '__main__':
  parser = optparse.OptionParser(usage=u'%prog [options] <base image> <directory>')
  parser.add_option('-o', '--out', help=u'target FILE (default <base>-mosaic-<precision>-<imagenum>-<width>x<height>.<ext>', default=None)
  parser.add_option('-p', '--precision', help=u'precision', default=5, type=int)
  parser.add_option('-n', '--num', dest='imgnum', type=int, 
    help='the final image will be composed of NUM*NUM small images')
  parser.add_option('--workdb', help=u'working db file',
    default='./data.db')
  parser.add_option('-t', '--threads', help=u'max thread num', type=int,
    dest='threadnum', default=3)
  parser.add_option('-w', '--work-dir', default=tmpdir)
  parser.add_option('--ext', help=u'image file extension', default='jpg',
    action='append', dest='exts')
  parser.add_option('--size', help=u'widthxheight of output', default=None)
  parser.add_option('--blend', help=u'blend result with the base - base gets PERCENT', default=[0], action='append')
  (options, args) = parser.parse_args()
  opts = {}

  if tmpdir != options.work_dir: tmpdir = os.tempnam(options.work_dir)
  if options.precision < 1 or options.precision > 10: 
    raise optparse.OptionValueError(u'precision must be between 1 and 10')
  if options.imgnum < 1 or options.imgnum > 1000:
    raise optparse.OptionValueError(u'imagenum must be between 1 and 1000')
  if options.threadnum < 1 or options.threadnum > 100: 
    raise optparse.OptionValueError(u'threadnum must be between 1 and 100')
  if options.size is not None: 
    try: opts['dest_size'] = tuple(map(int, options.size.split('x')[:2]))
    except:
      raise optparse.OptionValueError(u'size must be like 1280x1024 (two numbers separated by an "x")')
  else: 
    base_img = Image.open(args[0])
    opts['dest_size'] = base_img.size
    del base_img
  opts['dest_width'] = opts['dest_size'][0]
  opts['dest_height'] = opts['dest_size'][1]
  blends = set(map(int, options.blend)) 
  blends.remove(0)

  for k in ('threadnum', 'precision', 'imgnum'): 
    opts[k] = int(getattr(options, k))
  for k in ('workdb', 'work_dir', 'exts'): opts[k] = getattr(options, k)
  if len(args) < 2: raise optparse.OptParseError('2 args needed: base and dir')

  out_fn_pat = '%(base)s-mosaic-%(precision)02d-%(imgnum)02d-%(dest_width)dx%(dest_height)d-%(blend)s.%(ext)s'
  tmp = args[0].split('.')
  d = opts.copy()
  d['base'] = '.'.join(tmp[:-1])
  d['ext'] = tmp[-1]
  d['blend'] = '%d'
  del tmp
  out_fn = (options.out is None and [out_fn_pat % d] or [options.out])[0]

  files = []
  for name in args[1:]: files.extend(glob(name))

  try:
    img = main(args[0], files, **opts)
    t = time()
    img.save(out_fn % 0)
    print 'result: %s' % (out_fn % 0)
    print '\n%.03fs' % (time()-t)
    for blend in blends:
      base_blend = temp_read('base_blend.jpg')
      img2 = Image.blend(img, base_blend, float(blend)/100)
      img2.save(out_fn % blend)
      print 'result: %s' % (out_fn % blend)
  finally:
    temp_del()

