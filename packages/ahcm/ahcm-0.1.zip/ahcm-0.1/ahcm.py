#!/usr/bin/env python
""" ahcm - ad hoc configuration management tool

Usage:
    
    ahcm apply mypatch /prj/foo
    ahcm apply blah.txt foo.txt /prj/foo
    
    - Copy all files under directory mypatch over corresponding files in 
    /prj/foo. Do the same for blah.txt and foo.txt 
    If file doesn't exist under target dir, it's NOT created.
    
    ahcm today [places]
        
    - List all files changed today
    
    ahcm junk [places]
    
    - Remove all junk files (*~, *.bak...)
    
    
"""

# Copyright (c) Ville Vainio <vivainio@gmail.com>

# Licensed under the MIT license, see
#  http://www.opensource.org/licenses/mit-license.php

from path import path
import os,shutil,sys,time,fnmatch
import pickle
import mglob
import pprint

class DirLookup:
    def __init__(self,dir=None):
        self.filedict = {}
        if dir:
            self.pushfiles(dir)

    def pushfiles(self,dir):
        print "Pushing all in",dir
        i = 0
        #         for pathname,dirs,files in os.walk(dir):
        #             i+=1
        #             if i%20 == 0:
        #                 print path
        #                 print ".",
        #             pth = path(pathname)
        for f in path(dir).walkfiles():
            self.filedict[str(f.basename().lower())] = self.filedict.get(
                f.basename().lower(), []) + [f.abspath()]
            
    def lookup(self,f):
        return self.filedict[f.lower()]

    def exists(self,f):
        if self.filedict.has_key(f.lower()):
            return self.lookup(f)
        return None

    def allfiles(self):
        return self.filedict.items()


def getdiffs(old,new):
    diffs = os.popen("diff -c %s %s" % (old,new)).read()
    return diffs

_confirm_all = False

def confirm(prompt):
    global _confirm_all
    while 1:
        if not _confirm_all:
            r = raw_input(prompt)

        if _confirm_all or r == 'y' :
            return True
        elif r == 'a':
            _confirm_all = True
            return True
        elif r == 'n':
            return False
        
def similar_files(f1,f2):
    
    if f1.size != f2.size or f1.mtime != f2.mtime:
        return False
    if f1.text() != f2.text():
        return False
    return True

def find_good_match(pname, tries):
    pparts = pname.splitall()
    trieparts = [p.splitall() for p in tries]
    i = 0
    good = None

    while i < len(pparts):
        i+=1
        goodcount = 0
        for idx,trie in enumerate(trieparts):
            if trie[-i:] == pparts[-i:]:
                good = idx
                goodcount+=1
        if goodcount == 0:
            return None
        if goodcount == 1:
            print pname,"goodmatches",tries[good]
            return tries[good]
    return None

def expand_filelist(places):
    #return mglob.expand(places)
    pfiles = []
    for el in map(path,places):
        #print el
        if el.isdir():
            pfiles.extend(el.walkfiles())
        else:
            pfiles.append(el)
    return pfiles
    

def applypatch(*args): #patchdir, target):
    """ahcm apply [files...] target
    ahcm apply mypatch /prj/foo
    ahcm apply blah.txt foo.txt /prj/foo
    
    - Copy all files under directory mypatch over corresponding files in 
    /prj/foo. Do the same for blah.txt and foo.txt 
    If file doesn't exist under target dir, it's NOT created.
    """
    #print "Applying patch",patchdir,"to",target
    
    pfiles = expand_filelist(args[:-1])

    target = path(args[-1])
    
    lookup = DirLookup(target)
    #print lookup.allfiles()
    #patched = path(patchdir).
    #pdir = path(patchdir)
    #target= path(target)
    #pfiles = [pdir.relpathto(p) for p in pdir.walkfiles()]
        
    targets = []
    print pfiles
    for pf in pfiles:
        if not lookup.exists(pf.basename()):
            print "Ignoring:",pf
        else:
            lu = lookup.lookup(pf.basename())
            targets.append((pf, find_good_match(pf, lu)))
        
    print targets
    for src, tgt in targets:
        if tgt is None:
            print "Skipping, Multiple matches for",src
            continue
        print "%s -> TGT/%s" % (src, target.relpathto(tgt)),
        diffs = getdiffs(tgt,src)
        if not diffs:
            print "\t[unchanged]"
            continue
        if not _confirm_all:
            print diffs
        go = confirm("Copy (y/n/a): ")
        if go:
            print "Copying!"
            os.chmod(tgt, 0777) 
            shutil.copy2(src,tgt)

def changed_today(*places):
    """ahcm today [places]
        
    - List all files changed today
    """
    if not places:
        places = ['.']
    interval = 60 * 60 * 12 # 12 hours in seconds
    now = int(time.time())
    files = [(now-f.mtime, f) for f in expand_filelist(places) if now - f.mtime < interval]
    files.sort(reverse=True)
    def timestr(secs):
        hours = secs / 60
        mins = secs % 60
        if hours > 0:
            return "%d:%02d" % (hours, mins)
        return "%d min" % mins
    for t,f in files:
        print "%-40s %s" % (f, timestr(t/60))
    
def kill_junk(*places):
    """ahcm junk [places]
    
    - Remove all junk files (*~, *.bak...)
    """

    junk_pats = ['*~','*.bak','*.pyc']
    def isjunk(f):
        for pat in junk_pats:
            if fnmatch.fnmatch(f.basename(), pat):
                return True
            
    if not places:
        places = ['.']
    for f in expand_filelist(places):
        if isjunk(f):
            print f,'is junk'
            os.remove(f)
            
def lookup_files(*places):
    """ Quickly lookup files (a'la slocate) 
    
    ahcm lookup c:/my/dir - push all files in dir
    ahcm lookup blah - find a file with 'blah' in the name
    
    """
    filecache = 'c:/tmp/achm_filecache.pickle'
    if not places:
        places = ['.']
    if os.path.isfile(filecache):
        lookup = pickle.load(open(filecache))
    else:
        lookup = DirLookup()
    if os.path.isdir(places[0]):
        print "Pushing to lookup cache:",places[0]
        lookup.pushfiles(places[0])
        pickle.dump(lookup, open(filecache,'w'))
        return

    fpat = places[0]
    hits = lookup.exists(places[0])
    if hits:
        print "\n".join(hits)
    else:
        for k,v in lookup.allfiles():
            if fpat in k:
                print "\n".join(v)

def flatten_names(*args):    
    """ remove spaces and weird chars from file names """
    def flat_ch(ch):
        if not ord(ch) in range(128):
            return '_'
        if ch.isspace():
            return '_'
        return ch
    files = mglob.expand(args)
    pairs = [(path(f), path("".join(map(flat_ch, f)))) for f in files]
    changed = [(a,b) for (a,b) in pairs if a!=b]
    
    pprint.pprint(changed)
    if not raw_input('Enter y to commit:') == 'y':
        print "bailing out"
        return
    for old, new in changed:
        if not new.dirname().isdir():
            print "skipping",new," - dir does not exist"
        print "renaming",old
        old.rename(new)
    
    
def count_md5(*args):
    import md5
    #files = expand_filelist(args)
    files = [path(p) for p in mglob.expand(args)]
    print files
    out = "\n".join([md5.new(f.bytes()).hexdigest() + " " +f.basename() for f in files])
    print out
    return out


def rename_md5(*args):    
    """ Rename files by editing a text file with md5sums and file names
    
    First invocation of 'ahcm md5ren' will create the md5sums file, 
    edit it and invoke 'ahcm md5ren' again to commence with renames.
    """
    import md5
    fname = path('md5sums')
    if not fname.isfile():
        fname.write_text(count_md5(*(path('.').files())))
        print "Please edit file 'md5sums' and run again!"
        return
        
    md5f = fname.lines()
    ents = [l.rstrip().split(None,1) for l in md5f]
    realfiles = dict([(md5.new(f.bytes()).hexdigest(),f.basename()) for f in path('.').files()])
    print realfiles
    print ents
    for sum, newname in ents:
        oldname = realfiles.get(sum, None)
        if not oldname:
            print "skipping",newname
            continue
        if oldname == newname:
            print "Retain filename",oldname
            continue
        
        print "rename",oldname,'->',newname
        os.rename(oldname,newname)
        
        
    
        
def main():
    args = sys.argv[1:]
    cmd = args and args[0] or 'help'
    func = None
    
    commands = {
        'apply': applypatch,
        'today' : changed_today,
        'lookup' : lookup_files,        
        'junk' : kill_junk,
        'flatname' : flatten_names,
        'md5' : count_md5,
        'md5ren' : rename_md5  }
    
    if cmd == 'help':
        for c in commands:
            print '[%s]' % c
            print commands[c].__doc__
        return
    if cmd not in commands:
        print "Unknown command %s. Try one of help,%s instead." % (cmd, 
            ",".join(commands))
        return
    
    func = commands[cmd]
    
    apply(func, args[1:])
    
        

if __name__=="__main__":
    main()
