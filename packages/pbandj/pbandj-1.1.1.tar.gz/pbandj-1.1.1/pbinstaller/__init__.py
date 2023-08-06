#!python
# Zach Walker - zwalker at lcogt dot net
# Copyright (c) 2009 Las Cumbres Observatory.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import httplib
from tarfile import TarFile
from os import system, getcwd, chdir
from distutils.spawn import find_executable

BUILD_DEST = '.'
TAR_NAME = 'protobuf-%s.tar.gz'
VERSION_FILE = 'protoc_version'
TEST_OUT = 'protobuf_python_test.out'
PROTOC_SEARCH_DIRS = ['/bin', '/usr/bin', '/usr/local/bin']
    

def get_protobuf(dest, version='2.0.3', host='protobuf.googlecode.com', port=80, path='/files/protobuf-%s.tar.gz'):
    ''' Download a protobuf src package.  Default version is 2.0.3.
        http://protobuf.googlecode.com is the default host
        and the default path is /files/protobuf-%version%.tar.gz
    '''
    conn = httplib.HTTPConnection(host, port)
    conn.request('GET', path % version)
    resp = conn.getresponse()
    if resp.status != 200:
       raise Exception("Unable to retrieve %s.  Status was %d" % (path % version, resp.status))
    tarfile = open(dest, 'w')
    tarfile.write(resp.read())
    tarfile.close()
    return tarfile
    
def compile_protobuf(path):
    ''' Compile the protobuf project by executing
        confifure script followed by make with all
        defaults
    '''
    curpath = getcwd()
    chdir(path)
    system("./configure &> %s/protobuf_config.out" % curpath)
    system("make &> %s/protobuf_make.out" % curpath)
    chdir(curpath)
    
def install_protobuf(path):
    ''' Install the protobuf protoc binary
        by executing `make install`
    '''
    curpath = getcwd()
    chdir(path)
    system("make install &> %s/protobuf_make_install.out" % curpath)
    chdir(curpath)
    
def check_for_protobuf_python(version):
    ''' Check if a protobuf egg of the correct version is installed
        Return (found, version) where found is a flag,
        and version is like '2.0.3' or '' if not found
        or version is unknown.
    '''
    try:
        from google import protobuf
        prefix = 'protobuf-'
        postfix = '-py'
        if protobuf.__file__.find('egg') >= 0:
            if protobuf.__file__.find(prefix + version) >= 0:
                return (True, version)
            else:
                start = 'protobuf-'
                end = '-py'
                s = protobuf.__file__
                ver = protobuf.__file__[s.find(start) + len(start):s.find(end)]
                return (True, ver)
        else:
            return (True, '')
    except ImportError, err:
        return (False, '')

def chk_protoc_ver():
    ''' Check the protoc binary version
        Return output of `protoc --version` if found
        otherwise empty string
    '''
    protoc = find_executable("protoc")
    vstr = ""
    if protoc:
        #Check the version
        system(protoc + " --version > " + BUILD_DEST + VERSION_FILE)
        vfile = open(BUILD_DEST + VERSION_FILE)
        lines = vfile.readlines()      
        for line in lines:
            vstr += line
        return vstr

def install_protobuf_python(build_path, version):
    ''' Install the protobuf python egg
        by executing the setup.py install
        script found at build_path/python
    '''
    curpath = getcwd()
    chdir(build_path + "/python")
    #Run tests
#    system('python setup.py test' > BUILD_DEST + TEST_OUT)
#    tfile = open(BUILD_DEST + TEST_OUT)
#    tresults = tfile.readlinse()
#    for line in tresults:
#        if len(line) > 0 and line
    system('python setup.py bdist_egg &> %s/protobuf_setup.out' % curpath)
    system('python setup.py install &> %s/protobuf_install.out' % curpath)
    for p in sys.path:
        if p.endswith('site-packages'):
            sys.path.append(p + '/protobuf-%s-py%d.%d.egg' % (version,
                                                              sys.version_info[0],
                                                              sys.version_info[1]))
    chdir(curpath)
    
def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()
    
def install(version):
    BUILD_DEST = getcwd() + '/'
    #Add a few default places to look for protoc binary
    for dir in PROTOC_SEARCH_DIRS:
        if os.environ['PATH'].find(dir) < 0:
            os.environ['PATH'] = os.environ['PATH'] + (':%s' % dir)
    #See if protobuf python package is installed        
    installed, inst_ver = check_for_protobuf_python(version)
    print "Checking for protobuf python version %s: %s" % (version,
                                                           'ok' if installed and inst_ver == version else 'fail')
    if installed and inst_ver != version:
        print 'Found installed protobuf package with version: %s' % ('unknown' if inst_ver == '' else inst_ver)
        print 'This version may not work correctly.'
        yesno = raw_input('Continue with current version[Y/N].')
        if yesno.strip().upper() == 'N':
            installed = False
    if not installed:
        #Do you want to install proper version?
        install_egg = False
        install_bin = False
        yesno = raw_input('Unable to find python protobuf version %s required. Do you want to install it? [Y/N])' % version)
        if  yesno.strip().upper() == 'Y':
            install_egg = True
            try:
                #Download src package
                write('Attemping to downloading protoc src: ') 
                tarfile = get_protobuf(version=version, dest=(BUILD_DEST + (TAR_NAME % version)))
                write('ok\n')
                #Untar src pacakge
                write('Attempting to unpack src: ')
                tarfile = TarFile.gzopen(BUILD_DEST + (TAR_NAME % version))
                tarfile.extractall(BUILD_DEST)
                write('ok\n')
            except Exception, err:
                write('fail\n')
                print err
                sys.exit(1)

        if install_egg:
            write('Checking for compatible protoc binary version %s: ' % version)
            protoc_ok = False
            protoc_ver = chk_protoc_ver()
            if protoc_ver:
                if protoc_ver.find(version) >= 0:
                    write('ok\n')
                    protoc_ok = True   
                else:
                    write('fail\n')
                    print "Found protoc binary version %s but version %s is required" % (protoc_ver, version)
                    
            else:
                write('fail\n')
                print "Unable to find protoc binary."
            
            if not protoc_ok:
                print 'Compiling protoc binary...'
                compile_protobuf(BUILD_DEST + 'protobuf-' + version)
                yesno = raw_input("Do you want to install protoc binary? [Y/N]")
                if yesno.strip().upper() == 'Y':
                    write('Installing protoc binary...\n')
                    install_protobuf(BUILD_DEST + 'protobuf-' + version)
            
            protoc = find_executable('protoc')
            if not protoc:
                protoc = BUILD_DEST + 'protobuf-%s/src/protoc' 
            write('Installing protobuf python egg...')
            install_protobuf_python(BUILD_DEST + 'protobuf-' + version, version)
            write('ok\n')
            