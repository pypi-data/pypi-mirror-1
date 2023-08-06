#!/usr/bin/env python
# -*- coding: utf-8 -*-
#### Copyright (c) 2008 Clóvis Fabrício Costa - All rights reserved

"""Streaming rzip compression"""
import sys
import tempfile
import shutil
import subprocess
import os
import optparse
import tarfile
from cStringIO import StringIO

def buffered_read(fileobj, size):
    while True:
        block = fileobj.read(size)
        if block:
            yield block
        else:
            break


if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option('-v', '--block', action='store', dest='inputsize',
                   type='int', default=1048576, 
                   help='Compression Block Size in bytes, default 1 MiB')
    opt.add_option('-t', '--tar_bufsize', action='store', dest='bufsize',
                   type='int', default=10240, 
                   help='TarFile buffer Size in bytes, default 10 KiB')
    opt.add_option('-c', '--compress', action='store_true', dest='compress',
                   default=True, help='Compress (the default)')
    opt.add_option('-d', '--decompress', action='store_false', dest='compress',
                   help='Decompress')
    options, args = opt.parse_args()

    if options.compress:
        t = tarfile.open(mode='w|', fileobj=sys.stdout, 
                            bufsize=options.bufsize)
        for n, block in enumerate(buffered_read(sys.stdin, options.inputsize)):
            blockfile = tempfile.NamedTemporaryFile()
            blockfile.write(block)
            blockfile.flush()
            compressedblock_name = tempfile.mktemp()
            subprocess.call(['rzip', blockfile.name, '-k', '-9', '-o', 
                             compressedblock_name])
            blockfile.close() #deletes temporary file
            compressedblock = open(compressedblock_name, 'rb')
            info = t.gettarinfo(arcname='trzip.%d.block.rz' % n,
                                fileobj=compressedblock)
            t.addfile(info, fileobj=compressedblock)
            os.unlink(compressedblock_name)
        t.close()
    else:
        t = tarfile.open(mode='r|', fileobj=sys.stdin, 
                            bufsize=options.bufsize)
        for info in iter(t.next, None):
            compressedblock = t.extractfile(info)
            blockfile = tempfile.NamedTemporaryFile()
            shutil.copyfileobj(compressedblock, blockfile)
            blockfile.flush()
            uncompressedblock_name = tempfile.mktemp()
            subprocess.call(['rzip', blockfile.name, '-k', '-d', '-o', 
                             uncompressedblock_name])
            blockfile.close() #deletes temporary file
            for block in buffered_read(open(uncompressedblock_name), 
                                       options.inputsize):
                sys.stdout.write(block)
                sys.stdout.flush()
            os.unlink(uncompressedblock_name)
