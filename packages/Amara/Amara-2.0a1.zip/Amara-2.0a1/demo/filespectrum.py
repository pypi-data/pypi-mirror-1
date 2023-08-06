#Based on http://brainerror.net/scripts/python/duplocator/duplocator.py
#(see also http://brainerror.net/scripts/python/duplocator/ )
# Duplocator finds duplicate files and moves them to another directory.
# When two matching files are found the newest one is moved.
# Last modified on June 8, 2007 by John Hoogstrate

import os
import stat
import md5
import shutil
import sys
from time import gmtime, strftime

#import itertools
#import amara
from amara.writers.struct import *

ENC = 'iso-8859-1'

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if argv is None or len(argv) <= 1:
        print "Error: no path provided"
        return 2
    else:
        path = argv[1]
        
    if os.path.isdir(path):
        analyze(path)
        #moveDuplicates(duplicates)
    else:
        print "Error:", path, "is not a directory"
        return 2

def readfile(filename):
    """Read a file and return MD5 hash"""
    
    f = file(filename, 'rb');
    #print >> sys.stderr, "\nReading %s \n" % f.name;
    m = md5.new();
    readBytes = 1024; # read 1024 bytes per time
    totalBytes = 0;
    while (readBytes):
        readString = f.read(readBytes);
        m.update(readString);
        readBytes = len(readString);
        totalBytes+=readBytes;
    f.close();
    
    return m.hexdigest()


def walktree (top = ".", depthfirst = True):
    """Returns a list of directories and subdirectories for a specified path"""
    
    names = os.listdir(top)
    if not depthfirst:
        yield top, names
    for name in names:
        try:
            st = os.lstat(os.path.join(top, name))
        except os.error:
            continue
        if stat.S_ISDIR(st.st_mode):
            for (newtop, children) in walktree (os.path.join(top, name), depthfirst):
                #print 'Scanning ', newtop
                yield newtop, children
    if depthfirst:
        yield top, names


def ename(path):
    if os.path.isfile(path):
        return u'file'
    if os.path.isdir(path):
        return u'dir'
    if os.path.islink(path):
        return u'link'
    if os.path.ismount(path):
        #We should probably skip mount points
        return u'oops'
    #e.g. socket or device
    return 'other'
    

def analyze(path):
    """Identifies files as duplicates by comparing size and checksum"""
    sizes = dict()
    hashes = dict()
    duplicates = []

    def elem(basepath, fsnode):
        attrs = {}
        attrs[u'name'] = fsnode.decode(ENC)
        filepath = os.path.join(basepath, fsnode)
        if os.path.isfile(filepath):
            filesize = os.path.getsize(filepath)
            attrs[u'sz'] = filesize
            if sizes.get(filesize):
                try:
                    hash = readfile(filepath)
                except IOError, e:
                    print >> sys.stderr, e
                    hash = 'XXXUNKONWNXXX'
                attrs[u'hash'] = hash
                #print >> sys.stderr, "file:", filepath, " size:", filesize, " file2:", sizes.get(filesize), " hash:", hash
                if hashes.get(hash):
                    print >> sys.stderr, "duplicates:", hashes[hash], "and", filepath                  
                    attrs[u'dupe'] = hashes[hash].decode(ENC)
                    attrs[u'mtime'] = os.path.getmtime(filepath)
                    #move newest file to list of duplicates
                    #if os.path.getmtime(filepath) > os.path.getmtime(hashes[hash]):
                    #   duplicates.append(filepath) 
                    #else:
                    #   duplicates.append(hashes[hash])     
                
                else:
                    hashes[hash] = filepath
            else:
                sizes[filesize] = filepath
        if os.path.isdir(filepath):
            e = E(u'dir', attrs, ( elem(filepath, child) for child in os.listdir(filepath) ))
        else:
            e = E(ename(filepath), attrs)
        return e

    w = structwriter(indent=u"yes")
    w.feed(
    ROOT(
        E(u'files',
            ( E(u'dir', {u'path': path}, ( elem(path, child) for child in os.listdir(path) )) )
        )
    ))

    return# duplicates

def moveDuplicates(duplicates):
    """Moves found duplicates to another directory and writes to log file"""
    
    duplicatedir = './duplicates'
    logfile = 'duplocator.log';
    
    if not os.path.isdir(duplicatedir):
        os.mkdir(duplicatedir)
        
    for file in duplicates:
    
        if os.path.isfile(file):
        
            try:
                f = open(logfile, 'a')
                shutil.move(file, duplicatedir)
                print "moved", file
                f.write(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()) + ' moved file from ' + file + '\n')
                f.close()
            except IOError:
                print "error moving ", file
                
                
if __name__ == "__main__":
    sys.exit(main())