"""

Size Reporter and Dupe Finder

By Joe Koberg joe@osoft.us 2008-04-11

This program may be distributed under the terms of the GNU Public
License, v.3.



This program will:
    
    * Scan a directory tree, building an internal metadata tree.
    * Produce text reports of all metadata. (sizes and dates)
    * Produce a PDF graph of space consumption.
    * Find files that have identical content
    * Find directories that have identical content and structure.
    * Produce a text report of duplicate files and directories found.

"""


# standard library modules
from __future__ import with_statement

import bisect, bz2, colorsys, glob, hashlib, heapq, math
import logging, os, optparse, stat, sys, threading, time

from collections import defaultdict
from logging import debug, info, warning

HASHCLASS = hashlib.md5

MINIMUM_SIZE = 512
CHUNK_SIZE = 2**20
ROUND_ROBIN_SIZE = 2**20
ROUND_ROBIN_MAX_COUNT = 50

IGNOREFILES = ['Thumbs.db', '.DS_Store']
IGNOREDIRS = ['.AppleDouble']

PT = 1.0
INCH = 72 * PT
PAGE_HEIGHT = 13 * INCH
START_Y = 0.5 * INCH
START_X = 0.5 * INCH
INCREMENT_DIR = 1
DEPTH_INCREMENT = 0.25 * INCH
ONE_YEAR = 365 * 86400.0
MIN_CHILD = 0.3*PT
MIN_LABEL = 5*PT
LABEL_GAP = 0.5*INCH
PAGESIZE = (8.5,11)


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filename='size_and_dupe.log',
    filemode='a'
    )

debug('*** Loaded consolidated_dupe module')


# add-on modules
try:
    import reportlab
    import reportlab.pdfgen
    import reportlab.pdfgen.canvas
    PAGESIZE = reportlab.lib.pagesizes.legal
    PDF_AVAILABLE = True
except:
    warning("*** Could not load ReportLab PDF generation modules.  PDF output unavailable.")
    PDF_AVAILABLE = False
    




"""
class OrderedCollection(object):
    def __init__(self):
        self.collection = []
        self.seekpoint = 0
        
    def additem(self, key, item):
        if not self.collection:
            self.collection.append( (key,[item]) )
            return 0
        insertpoint = bisect.bisect_left(self.collection, (key,None))
        (ckey, citems) = self.collection[insertpoint]
        if key == ckey:
            citems.append(item)
        else:
            self.collection.insert(insertpoint, (key,[item]) )
        return insertpoint
"""        
        

class FileIndex(object):
    def __init__(self):
        self.lock = threading.Lock()
        with self.lock:
            self.alldirs = {}
            self.dupes = {}
            self.bysize = defaultdict(list)
        
    def addFile(self, f):
        with self.lock:
            self.bysize[f.size].append(f)
        
    def addDir(self, name, d):
        with self.lock:
            self.alldirs[name] = d
       
    def getDir(self, *args, **kw):
        with self.lock:
            return self.alldirs.get(*args, **kw)
            
    def addDupeGroup(self, size, hsh, files):
        with self.lock:
            self.dupes[(size,hsh)] = files
            for f in files:
                for p in f.parents:
                    p.hasDupes = True
        
        



class DirectoryWalk(object):
    @classmethod
    def set_semaphore(cls, value=5):
        cls.finish_semaphore_value = value
        cls.finish_semaphore = threading.Semaphore(value)
        
    @classmethod
    def wait_for_walks(cls, func=lambda d:None):
        for n in range(cls.finish_semaphore_value):
            cls.finish_semaphore.acquire()
        try:
            result = func()
        finally:
            for n in range(cls.finish_semaphore_value):
                cls.finish_semaphore.release()
        return result
        
    def __init__(self, dirname, fileindex=None, dirdone_callback=None):
        self.dirname = dirname
        if not fileindex:
            fileindex = FileIndex()
        self.fileindex = fileindex
        if not dirdone_callback:
            self.dirdone_callback = lambda idx,d,fs: None
        else:
            self.dirdone_callback = dirdone_callback
            
    def indexFile(self, f):
        if self.fileindex:
            self.fileindex.addFile(f)
            
    def indexDir(self, name, d):
        if self.fileindex:
            self.fileindex.addDir(name, d)
        
    def walk(self, threaded=False):                
        if threaded:
            self.walk_lock = threading.Lock()
            def thread_target():
                with self.walk_lock:
                    with self.finish_semaphore:
                        self.walkBase()
            self.thread = threading.Thread(target=thread_target)
            self.thread.start()
        else:
            self.walkBase()

    def walkBase(self):
        info('Beginning walk of %s'%(self.dirname,))
        for index, (fulldirname, subdirs, files) in enumerate(os.walk(self.dirname, topdown=False)):
            parentpath, dirname = os.path.split(fulldirname)
            if dirname in IGNOREDIRS:
                continue
                
            ffiles = []
            for filename in files:
                try:
                    if filename in IGNOREFILES:
                        continue
                    fullfn = os.path.join(fulldirname, filename)
                    if os.path.islink(fullfn):
                        continue
                    try:
                        filestat = os.stat(fullfn)
                    except WindowsError:
                        warning("File error: %s"%(fullfn,))
                    ff = File(fullfn, filestat)
                    self.indexFile(ff)
                    ffiles.append(ff)
                except WindowsError:
                    warning("filename too long: %s"%(fullfn,))
                    continue
                    
            ssubs = [] 
            for subdir in subdirs:
                if subdir in IGNOREDIRS:
                    continue
                fullsubdname = os.path.join(fulldirname,subdir)
                if os.path.islink(fullsubdname):
                    continue
                subd = self.fileindex.getDir(fullsubdname, None)
                if not subd:
                    warning('Reached %s before subdir %s'%(fulldirname, fullsubdname))
                else:
                    ssubs.append(subd)
                    
            dd = Directory(fulldirname, children=ssubs+ffiles)
            
            self.indexDir(fulldirname, dd)
            if fulldirname == self.dirname:
                self.topdir = dd
                
            self.dirdone_callback(index, dd, ffiles)
            
            if index % 100 == 0:
                info('%d directories walked. on %s'%(index, fulldirname))
            


class FileHashingMixin(object):
    def __init__(self):
        self.fullhash = None
        self.chunksread = 0
        self.finished = False    
        
    def getHash(self):
        if not self.fullhash:
            return None
        return self.fullhash.hexdigest()
            
    def nextchunk(self):
        if not self.fullhash:
            self.fullhash = HASHCLASS()
        if not self.finished:
            if self.chunksread == 0:
                self.fobj = open(self.fullname, 'rb')
                self.openfiles += 1
            if self.chunksread*CHUNK_SIZE >= self.size:
                self.fobj.close()
                self.openfiles -= 1
                self.finished = True
            else:
                chunk = self.fobj.read(CHUNK_SIZE)
                self.fullhash.update(chunk)
                self.chunksread += 1
        return self.fullhash.hexdigest()
            
    def allchunks(self):
        while not self.finished:
            chunk = self.nextchunk()
        return self.fullhash.hexdigest()

        
        
class FileGraphMixin(object):
    sortorder = 10
    leaf = True
        
    @property
    def total_height(self):
        if not self.parent:
            return PAGE_HEIGHT
        if self.parent.size:
            mysize = self.size
            if mysize > self.parent.size:
                raise Exception("File larger than containing directory")
            my_frac = float(mysize) / self.parent.size
            return my_frac * self.parent.total_height
        else:
            return self.parent.total_height/len(self.parent.children)  

    @property
    def depth(self):
        if not hasattr(self, 'parent') or not self.parent:
            return 0
        return self.parent.depth + 1

        
        
class File(FileHashingMixin, FileGraphMixin):
    openfiles = 0
    parent = None
    def __init__(self, fullname, statinfo):
        path, self.basename = os.path.split(fullname)
        self.statinfo = statinfo        
        #Node.__init__(self, fullname, statinfo)
        FileHashingMixin.__init__(self)
        FileGraphMixin.__init__(self)

    @property
    def dupe_repr(self):
        return "File(%012d,%s)"%(self.size, self.getHash())

    @property
    def parents(self):
        if self.parent:
            return [self.parent] + self.parent.parents
        else:
            return []

    size = property(lambda self: self.statinfo[stat.ST_SIZE])
    ctime = property(lambda self: self.statinfo[stat.ST_CTIME])
    mtime = property(lambda self: self.statinfo[stat.ST_MTIME])
    atime = property(lambda self: self.statinfo[stat.ST_ATIME])
    uid = property(lambda self: self.statinfo[stat.ST_UID])
    gid = property(lambda self: self.statinfo[stat.ST_GID])
    ino = property(lambda self: self.statinfo[stat.ST_INO])
    nlink = property(lambda self: self.statinfo[stat.ST_NLINK])
    dev = property(lambda self: self.statinfo[stat.ST_DEV])
    dates = property(lambda self: (self.ctime, self.mtime, self.atime))        
        
    @property
    def fullname(self):
        if self.parent:
            return os.path.join(self.parent.fullname, self.basename)
        return self.basename
        
    @property
    def path(self):
        if self.parent:
            self.parent.fullname
        return ''
        
    @property
    def latest_date(self):
        return sorted(self.dates)[-1]
        


class DirectoryGraphMixin(FileGraphMixin):
    sortorder = 20
    leaf = False
    
    def sortKey(self, node):
        return node.size
    
    def children_and_heights(self, y0=START_Y, recursive=False):
        self.children.sort(key=self.sortKey, reverse=True)
        children = self.children
        cur_height = y0
        for child in self.children:
            if child.total_height < MIN_CHILD:
                continue
            new_height = cur_height + (INCREMENT_DIR * child.total_height)
            if recursive and not child.leaf:
                for tup in child.children_and_heights(cur_height, recursive):
                    yield tup
            yield (child, cur_height, new_height, child.depth)
            cur_height = new_height

            
            
class DirectorySizeReportMixin(object):
    def __init__(self):
        self.filecount = 0
        self.filecount_local = 0
        self.dircount = 0
        self.dircount_local = 0
        self.size_local = 0
        self.size_accum = 0
        self.size_accum_exts = defaultdict(int)
        self.size_accum_exts_local = defaultdict(int)        
        self.latest_date = 0.0
        
    def addChild(self, child):
        childSize = child.size
        if isinstance(child, Directory):
            self.dircount_local += 1
            self.dircount += (child.dircount + 1)
            self.filecount += child.filecount
            for fext, size in child.size_accum_exts.items():
                self.size_accum_exts[fext] += size
        else:
            self.filecount += 1
            self.filecount_local += 1
            fname, fext = os.path.splitext(child.basename)
            self.size_accum_exts[fext] += childSize
            self.size_accum_exts_local[fext] += childSize
            self.size_local += childSize
        if self.latest_date < child.latest_date:
            self.latest_date = child.latest_date
        self.size_accum += childSize
        
        
class Directory(DirectorySizeReportMixin, DirectoryGraphMixin):
    parent = None
    hasDupes = False
    def __init__(self, fullname, children):
        self.fullname = fullname
        #Node.__init__(self, fullname, statinfo)
        DirectorySizeReportMixin.__init__(self)
        DirectoryGraphMixin.__init__(self)
        self.children = []
        self.repr_str = ''
        self.addChildren(children)
        
    @property
    def parents(self):
        if self.parent:
            return [self.parent] + self.parent.parents
        else:
            return []
            
    @property
    def path(self):
        return os.path.split(self.fullname)[0]
    
    @property
    def dupe_repr(self):
        if not self.repr_str:
            self.children.sort(key=lambda c: c.dupe_repr)
            self.repr_str = "Dir(%s)"%( '[' + ','.join([c.dupe_repr for c in self.children]) + ']' )
        return self.repr_str
                
    def addChild(self, child):
        child.parent = self
        self.children.append(child)
        DirectorySizeReportMixin.addChild(self, child)
        self.repr_str = ''
        
    def addChildren(self, children):
        for child in children:
            self.addChild(child)
            
    def __iter__(self):
        return iter(self.children)
        
    size = property(lambda self: self.size_accum)

        
        
"""        
def allEqual(seq):
    if len(seq)<2:
        return True
    exemplar = seq[0]
    for idx in xrange(1,len(seq)):
        if seq[idx] != exemplar:
            return False
    return True
            
           
def namePrefixer(fnames):
    # going to return origname, [deletenames], [unsure]
    if not fnames:
        return None, [], []
    if len(fnames)<2:
        return fnames[0], [], []
    namemap = {}
    basemap = {}
    deletes = []
    unsures = []
    for fname in fnames:
        path, name = os.path.split(fn)
        base, extension = os.path.splitext(name)
        lowbase = base.lower()
        namemap.setdefault(name, []).append(fname)
        basemap.setdefault(lowbase, []).append(fname)
        fns.append(lowbase)
    fns.sort(key=lambda i: '%013d%s'%(len(i),i))
    first, rest = fns[0], fns[1:]
    lenfirst = len(first)
    for item in rest:
        if item == first:
            deletes.append(item)
        elif item[0:lenfirst] == first:
            deletes.append(item)
        else:
            unsures.append(item)
    return first, deletes, unsures        

    
    
   
class DeDupeHeuristic(object):
    def inSameDir(self, func):
        def ff(flist):            
            example = flist[0].path
            for f in flist[1:]:
                if f.path != example:
                    return None
            return func(flist)
        return ff
        
    def evalfuncs(self):
        return (
            (100, self.inSameDir(self.eval_substring)),
            (100, self.inSameDir(self.eval_dates)),
            (  0, self.eval_substring),
            (  0, self.eval_dates),
        )
        
    def evaluate_dupelist(self, flist):
        result = None
        for weight, evalfunc in self.evalfuncs():
            result = evalfunc(flist)
            if result:
                return result
                
    def eval_substring(self, flist):
        flist.sort(key=lambda f: (f.path, len(f.base), f.base))
        shortest = flist[0]
        rest = flist[1:]
        for f in rest:
            if shortest.base not in f.base:
                return None
        return f, rest
        
    def eval_samedir_substring(self, flist):
        splits = [(f,f.split()) for f in flist]
        splits.sort(key=lambda f:(ffpfn[1][0],len(ffpfn[1][1]),ffpfn[1][1]))
        cfn, cdir, cfile = splits[0]
        for tfn, tdir, tfile in splits[1:]:
            if tdir != cdir:
                return None #cant comment on files not in same dir
            if cfile not in tfile:
                return None #file not a substring of other file names
        return cfn, [f for f,fpfn in splits[1:]]     
        
    def get_file_date(self, fname):
        return os.stat(fname)[stat.ST_CTIME]
        
    def eval_dates(self, flist):
        # earliest date wins
        flist.sort(key=self.get_file_date)
        return flist[0], flist[1:]

        
""" 



            
class LargestSubtreeDupeFinder(object):
    def parentAlreadyFound(self, d):
        for p in d.parents:
            for dlist in self.largest.values():
                if p in dlist:
                    return p                

    def analyze(self, fileindex):
        self.fileindex = fileindex
        self.reprmap = defaultdict(list)
        self.largest = defaultdict(list)
        self.dupedreprs = []
        for path, d in self.fileindex.alldirs.items():
            if d.hasDupes:
                r = d.dupe_repr
                self.reprmap[r].append(d)
                if len(self.reprmap[r]) == 2:
                    self.dupedreprs.append(r)
        
        self.dupedreprs.sort(key=len, reverse=True)
        
        for duperepr in self.dupedreprs:
            dupes = self.reprmap[duperepr]
            for dupe in dupes:
                if not self.parentAlreadyFound(dupe):
                    self.largest[duperepr].append(dupe)
        return self.largest.values()

        
class FindDupes(object):
    def __init__(self, fileindex, prefix, tstamp):
        self.fileindex = fileindex
        self.sizedict = fileindex.bysize
        
        log = open('%s_%s_dupes.txt'%(prefix, tstamp), 'w')
        for size, hsh, files in self.findDupes():
            self.fileindex.addDupeGroup(size, hsh, files)
            log.write('((%d,%s,%d), [\n'%(size,repr(hsh),len(files)))
            log.write( ',\n'.join([repr(f.fullname) for f in files]) + '\n]),\n\n')
        log.close()
        
        log = open('%s_%s_dupedirs.txt'%(prefix, tstamp), 'w')
        dupedirs = LargestSubtreeDupeFinder().analyze(self.fileindex)
        for dirset in dupedirs:
            log.write('[\n' + ',\n'.join([repr(d.fullname) for d in dirset]) + '\n],\n\n')
        log.close()
        
    def findDupes(self):
        sizes = self.sizedict.keys()
        sizes.sort()
        for size in sizes:
            if size < MINIMUM_SIZE:
                continue
            sizegroup = self.sizedict[size]
            if size >= ROUND_ROBIN_SIZE and len(sizegroup)<=ROUND_ROBIN_MAX_COUNT:
                dupegroups = self.examineGroupRoundRobin(sizegroup)
            else:
                dupegroups = self.examineGroupInTurn(sizegroup)
            for (hsh, files) in dupegroups.items():
                yield (size, hsh, files)
            
    def examineGroupInTurn(self, sizegroup):
        hashes = defaultdict(list)
        for f in sizegroup:
            fhsh = f.allchunks()
            hashes[fhsh].append(f)
        dupegroups = dict([(hsh,grp) for (hsh,grp) in hashes.items() if len(grp)>1])
        return dupegroups

    def multipleNotFinished(self, files):
        count = 0
        for f in files:
            if not f.finished:
                count += 1
            if count > 1:
                return True        
        
    def workRemains(self, hashgroups):
        for hsh,grp in hashgroups.items():
            if self.multipleNotFinished(grp):
                return True
        
    def examineGroupRoundRobin(self, sizegroup):
        hashgroups = {'':sizegroup}
        while hashgroups:
            newhashgroups = defaultdict(list)
            for prevhsh, files in hashgroups.items():
                for f in files:
                    f.nextchunk()
                    newhashgroups[f.getHash()].append(f)
            hashgroups = dict([(hsh,grp) for (hsh,grp) in newhashgroups.items() if len(grp)>1])
            if not self.workRemains(hashgroups):
                return hashgroups
        return {}
 
     

    
    
class SizeReporter(object):
    def __init__(self, tstamp, prefix='sizereport', suffix='txt', compress=False):
        self.tstamp = tstamp
        if compress:
            opn = bz2.BZ2File
            suffix += '.bz2'
        else:
            opn = open

        info('--- size_reporter report generating run starting.')

        self.outf_s = opn('%s_%s_dirs.%s'%(prefix,tstamp,suffix), 'w')
 
        self.outf_s.write('DirID\tParentDirName\tDirName\tLocalDirs\tDirs\tLocalFiles\tFiles\tLocalSize\tTotalSize\n')
        
        self.outf_e = opn('%s_%s_extensions.%s'%(prefix,tstamp,suffix),'w')
        self.outf_e.write('DirID\tExtension\tLocalSize\tTotalSize\n')
        
        self.outf_f = opn('%s_%s_files.%s'%(prefix,tstamp,suffix), 'w')
        self.outf_f.write('DirID\tFileName\tExtension\tFileSize\tCreated\tModified\tAccessed\n')
        
    def formatTime(self, tstamp, format='%Y-%m-%d %H:%M:%S', fracdigits=3, conv=time.gmtime):
        if not fracdigits:
            return time.strftime(format, conv(tstamp))
        intpart = int(tstamp)
        fracpart = tstamp - intpart
        str_head = time.strftime(format, conv(intpart))
        fstr = '%0.' + str(int(fracdigits)) + 'f'
        str_tail = (fstr%(fracpart,))[1:]
        return str_head + str_tail

        
    def report_dir_callback(self, index, d, fs):
        self.outf_s.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(index,d.path, d.fullname,
                    d.dircount_local, d.dircount, d.filecount_local,d.filecount, d.size_local, d.size))
        
        extensions = d.size_accum_exts.keys()
        for extension in extensions:
            size = d.size_accum_exts[extension]
            size_local = d.size_accum_exts_local.get(extension, 0)
            self.outf_e.write('%d\t%s\t%d\t%d\n'%(index, extension, size_local, size))
            
        for f in fs:
            path, name = os.path.split(f.fullname)
            dummy, ext = os.path.splitext(name)
            try:
                acc, mod, creat = [self.formatTime(t) for t in f.dates]
            except ValueError:
                warning('Invalid file date for %s'%(f.fullname,))
                continue
            self.outf_f.write('%d\t%s\t%s\t%d\t%s\t%s\t%s\n'%(
                index, name, ext, f.size, creat, mod, acc))
                
        self.outf_s.flush()
        self.outf_e.flush()
        self.outf_f.flush()

            
    def close_report(self):
        self.outf_s.close()
        self.outf_e.close()
        self.outf_f.close()




     
    
    
    
class Color(tuple):
    @classmethod
    def from_hls(Self, hls):
        return Self(colorsys.hls_to_rgb(*hls))
        
    @classmethod
    def from_hsv(Self, hsv):
        return Self(colorsys.hsv_to_rgb(*hsv))

    def __init__(self, rgb):
        tuple.__init__(self, rgb)
        for v in self:
            if v < 0.0 or v>1.0:
                raise ValueError('Color RGB values must be in range 0.0 to 1.0 (got %s)'%(self,))
        
    def __repr__(self):
        return 'Color(%0.3f, %0.3f, %0.3f)'%self
        
    def to_hls(self):
        return colorsys.rgb_to_hls(*self)
        
    def to_hsv(self):
        return colorsys.rgb_to_hsv(*self)
        
    def to_html(self):
        crgb = [int(v * 255) for v in self]
        return '#%02x%02x%02x'%crgb
        
    def huerotate(self, angle, tofunc, fromfunc, circle=1.0):
        angle = angle / circle
        h, x, y = tofunc()
        newh = (h + angle) % circle
        return fromfunc((newh,x,y))
        
    def hlsrotate(self, angle, circle=1.0):
        return self.huerotate(angle, 
                               tofunc=self.to_hls,
                               fromfunc=self.from_hls,
                               circle=circle
                               )
                               
    def hsvrotate(self, angle, circle=1.0):
        return self.huerotate(angle,
                               tofunc=self.to_hsv,
                               fromfunc=self.from_hsv,
                               circle=circle
                               )

Color.red =   Color((1,0,0))
Color.green = Color((0,1,0))
Color.blue =  Color((0,0,1))
Color.black = Color((0,0,0))
Color.white = Color((1,1,1))
    
    

class PDFRender(object):
    def __init__(self, fname, defaultStrokeColor=Color.black, defaultLineWidth=MIN_CHILD*0.25, pagesize=PAGESIZE):
        self.defaultStrokeColor = defaultStrokeColor
        self.defaultLineWidth = defaultLineWidth 
        self.canvas = reportlab.pdfgen.canvas.Canvas(fname,pagesize=pagesize)
        self.canvas.setLineWidth(self.defaultLineWidth)
        
    def rect(self, x0,y0, x1,y1, color=Color.red, fill=True,stroke=True):
        self.canvas.setStrokeColorRGB(*self.defaultStrokeColor)
        self.canvas.setFillColorRGB(*color)
        width = x1 - x0
        height = y1 - y0
        self.canvas.rect(x0,y0, width,height, fill=fill, stroke=stroke)
        
    def text(self, x0,y0,  text, height, fontname='Helvetica', color=Color.black, fill=True, stroke=False):
        self.canvas.setFillColorRGB(*color)
        self.canvas.setFont(fontname, height)
        self.canvas.drawString(x0,y0, text)
        
    def save(self):
        self.canvas.showPage()
        self.canvas.save()    
    
    
class SizeReportPDF(object):
    def __init__(self, rootdir):
        self.max_x = 0.0
        self.rootdir = rootdir
        
    def color_by_date(self, date, hue):
        nodeage = min(3*ONE_YEAR, (max(0.0, time.time() - date)))
        fraction = nodeage/(3*ONE_YEAR)
        saturation = 1.0
        lightness =  0.25 + (fraction * 0.75)
        return Color.from_hls((hue, lightness, saturation))
        
    def pdf_draw_node(self, pdf, node, y0, y1, depth):
        x0 = (depth * DEPTH_INCREMENT) + START_X
        x1 = ((depth+1) * DEPTH_INCREMENT) + START_X
        self.max_x = max(x1, self.max_x)
        hue = (y0-START_Y)/PAGE_HEIGHT
        fillcolor = self.color_by_date(node.latest_date, hue)
        strokewidth = MIN_CHILD/3.0
        pdf.rect(x0,y0, x1,y1, fillcolor)
            
    def pdf_draw_text(self, pdf, x0,y0, size, text):
        pdf.text(x0,y0, text, size)

    def generatePDF(self, filename):
        labels = []
        pdf = PDFRender(filename)
        for node, y0, y1, depth in self.rootdir.children_and_heights(recursive=True):
            self.pdf_draw_node(pdf, node, y0, y1, depth)
            if node.total_height >= MIN_LABEL:
                labels.append((y0, node, depth))
        label_x = self.max_x + LABEL_GAP
        for y0, node, depth in labels:
            if node.leaf:
                sizetext = '% 10d'%(node.size,)
            else:
                sizetext = ''
            self.pdf_draw_text(pdf, label_x,y0, MIN_LABEL,
                               node.fullname.replace('&', '&amp;')+' '+sizetext)
        pdf.save()
    

        



def main():
    print ("""
 Size Reporter, by Joe Koberg, joe@osoft.us 2008-02-01

 Distributed under the terms of the GNU PUBLIC LICENSE version 3.
 This license grants you certain rights, and requires that this
 program be distributed to you with source code included. 
 Please find the full license at <http://www.gnu.org/licenses/>

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

""")
    tstamp = time.strftime('%Y%m%d_%H%M%S')
    
    def pdf_option_callback(option, opt_str, value, parser):
        if not PDF_AVAILABLE:
            raise optparse.OptionValueError("%s: PDF libraries are not installed."%(opt_str,))
        parser.values.size_pdf = True
    
    parser = optparse.OptionParser()
    parser.add_option("-p", "--size-pdf",  action="callback", callback=pdf_option_callback, dest="size_pdf",   default=PDF_AVAILABLE,
                      help="Produce graphical size report as a PDF file.")
    
    parser.add_option("-s", "--size-text", action="store_true", dest="size_text",  default=True,
                      help="Produce tab-delimited size report as a text file.")
    
    parser.add_option("-d", "--dupe-text", action="store_true", dest="dupe_text",  default=False,
                      help="Produce duplicate file report as a python text file.")
    
    parser.add_option("-t", "--threaded",         action="store_true", dest="threaded", default=False,
                      help="Scan directory arguments in parallel.")

    parser.add_option("-m", "--max-parallel",    action="store", dest="max_walkers", type="int", default=5,
                      help="Maximum number of directories to scan in parallel.")

    parser.add_option("-z", "--bzip2",         action="store_true", dest="do_compress", default=False,
                      help="Write size report files as bzip2'ed text files.")
    
    parser.add_option("-f", "--file-prefix",    action="store", dest="file_prefix",default="sizereport_",
                      help="Set the filename prefix for the produced files.")
    
    
    options, args = parser.parse_args()
    fileindex = FileIndex()
    walkers = []
    dirdone_callback = None
    interactive = False
    
    if not args:
        interactive = True
        dirname = raw_input("Enter directory name to scan: ")
        if not dirname or not os.path.isdir(dirname):
            sys.exit(2)
        args = [dirname]
        
    if options.max_walkers:
        DirectoryWalk.set_semaphore(options.max_walkers)
    
    if args and (options.size_text or options.size_pdf):
        sizereport = SizeReporter(tstamp, prefix=options.file_prefix, compress=options.do_compress)
        dirdone_callback = sizereport.report_dir_callback    
        
    for directory in args:
        print "Scanning %s"%(directory,)
        w = DirectoryWalk(directory, fileindex, dirdone_callback=dirdone_callback)
        walkers.append(w)
        w.walk(threaded=options.threaded)
        
    if options.threaded:
        DirectoryWalk.wait_for_walks()
        
    if options.size_text:
        sizereport.close_report()
    
    if options.size_pdf:
        for idx, w in enumerate(walkers):
            print "Generating PDF for %s..."%(w.dirname,)
            s = SizeReportPDF(w.topdir)
            s.generatePDF('%s_%s_%d.%s'%(options.file_prefix,tstamp,idx,'pdf'))
        
    if options.dupe_text:
        print "Scanning for duplicate files..."
        d = FindDupes(fileindex, options.file_prefix, tstamp)
        #l = LargestSubtreeDupeFinder(d)
        #subtrees = l.analyze()        
        
    if interactive:
        raw_input( "Finished scanning. Press <ENTER> to continue.") 
    
if __name__=="__main__":
    main()