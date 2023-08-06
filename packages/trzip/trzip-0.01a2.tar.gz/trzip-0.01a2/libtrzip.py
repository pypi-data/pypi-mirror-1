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

def buffered_read(fileobj, size):
    while True:
        block = fileobj.read(size)
        if block:
            yield block
        else:
            break

def compress_stream(inputstream, outputstream, bufsize, inputsize):
    t = tarfile.open(mode='w|', fileobj=outputstream, 
                        bufsize=bufsize)
    for n, block in enumerate(buffered_read(inputstream, inputsize)):
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

def uncompress_stream(inputstream, outputstream, bufsize):
    t = tarfile.open(mode='r|', fileobj=inputstream, 
                        bufsize=bufsize)
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
            outputstream.write(block)
            outputstream.flush()
        os.unlink(uncompressedblock_name)

def main():
    opt = optparse.OptionParser()
    opt.add_option('-b', '--block', action='store', dest='inputsize',
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
        compress_stream(sys.stdin, sys.stdout, 
                                 options.bufsize, options.inputsize)
    else:
        uncompress_stream(sys.stdin, sys.stdout, options.bufsize)

if __name__ == '__main__':
    main()
    