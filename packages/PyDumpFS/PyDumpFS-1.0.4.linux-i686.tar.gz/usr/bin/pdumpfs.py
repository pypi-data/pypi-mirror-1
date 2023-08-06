#!/usr/bin/python
# -*- coding: utf8 -*-
import sys
import os
import time
import shutil
import math
import filecmp
import re
import sha
import shelve
import gettext
__author__ = "HASEGAWA Masahiro <hasegawa@mapse.eng.osaka-u.ac.jp>"
__version__ = "1.0.4"
__copyright__ = "Copyright (c) 2007-2009 MASA.H"
__license__ = "New-style BSD"

try:
    gettext.install('PyDumpFS',unicode=1)
except IOError:
    _=lambda str: str

class Matcher:
    def exclude(self, path):
        pass

class NullMatcher(Matcher):
    def exclude(self, path):
        return 0

class SizeMatcher(Matcher):
    def __init__(self, size_):
        self.size=self.calc_size(size_)
    def calc_size(self, size_):
        tmp=int(re.compile("^[0-9]+").search(size_).group(0))
        if re.compile("^[0-9]+[kK]").search(size_):
            tmp=tmp*1024
        elif re.compile("^[0-9]+[mM]").search(size_):
            tmp=tmp*1024*1024
        elif re.compile("^[0-9]+[gG]").search(size_):
            tmp=tmp*1024*1024*1024
        return tmp
    def exclude(self, path):
        stats=os.stat(path)
        if stats.st_size>self.size:
            return True
        else:
            return False

class NameMatcher(Matcher):
    def __init__(self, pattern_):
        self.pattern=re.compile(pattern_)
    def exclude(self, path):
        if self.pattern.search(path):
            return True
        else:
            return False

class pdumpfs:
    """Pseudo DumpFS
    this make backup like plan9's dumpfs
    """
    src=""
    dest=""
    rev_path=""
    latest=""
    matcher=[]
    hash_db=None
    def __init__(self, src_, dest_, verbose=0):
        self.src=os.path.abspath(os.path.expanduser(
                                                os.path.expandvars(src_)))
        self.dest=os.path.abspath(os.path.expanduser(
                                                os.path.expandvars(dest_)))
        basename_=os.path.split(self.src)[1]
        if basename_=="":
            basename_=os.path.split(os.path.split(self.src)[0])
        self.latest=os.path.join(self.dest, "latest", basename_)
        self.matcher.append(NullMatcher())
        self.verbose=verbose
        self.hash_db=shelve.open(os.path.join(self.dest,".hash"),"c")
    def _make_link(self, path):
        if self.verbose>1:
            print _("make hardlink:")+"%s"%path
        dest_=path.replace(self.latest, self.rev_path, 1)
        if not os.path.exists(os.path.split(dest_)[0]):
            os.makedirs(os.path.split(dest_)[0])
        os.link(path,dest_)
    def _copy_symlink(self, path):
        """Copy symbolic link"""
        linkto=os.readlink(path).replace(self.src, "")[1:]
        if os.path.exists(os.readlink(path)):
            while 1:
                reflinkto=os.path.abspath(os.path.join(os.path.split(path)[0],
                                                                linkto))
                if os.path.abspath(os.readlink(path))==reflinkto:
                    break
                linkto=os.path.join("..", linkto)
            if self.verbose>1:
                print _("make symboliclink:")+"%s"%path
            os.symlink(linkto, path.replace(self.src, self.rev_path, 1))
    def make_copy(self, path):
        if self._exclude(path):
            if self.verbose>0:
                print _("exclude file:")+"%s"%path
        elif self._is_internal_link(path):
            self._copy_symlink(path)
        elif os.path.isdir(path):
            self._copy_dir(path)
        else:
            if self.verbose>1:
                print _("copy:")+"%s"%path
            dst=path.replace(self.src, self.rev_path, 1)
            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            dst_r=self._find_hash(path)
            if dst_r:
                os.link(dst_r,dst)
            else:
                shutil.copy2(path, dst)
            self._regist_hash(dst)
    def make_rev_path(self):
        self.ntime=int(math.floor(time.time()))
        self.rev_path=os.path.join(self.dest, ".rev", `self.ntime`)
        while 1:
            if os.path.exists(self.rev_path):
                self.ntime+=1
                self.rev_path=os.path.join(self.dest, ".rev", `self.ntime`)
            else:
                break
        if self.verbose>0:
            print _("make directory:")+"%s"%self.rev_path
        os.makedirs(self.rev_path)
        self.tmp_path=os.path.join(self.dest, 
                            time.strftime("%Y", time.localtime(self.ntime)), 
                            time.strftime("%m", time.localtime(self.ntime)), 
                            time.strftime("%d", time.localtime(self.ntime)))
        if not os.path.exists(self.tmp_path):
            if self.verbose>0:
                print _("make directory:")+"%s"%self.tmp_path
            os.makedirs(self.tmp_path)
        basename_=os.path.split(self.src)[1]
        if basename_=="":
            basename_=os.path.split(os.path.split(self.src)[0])
        self.tmp_path2=os.path.join(self.tmp_path, basename_)
        if os.path.exists(self.tmp_path2):
            os.remove(self.tmp_path2)
        os.symlink(self.rev_path, self.tmp_path2)
    def update_latest_link(self):
        if not os.path.exists(os.path.join(self.dest, "latest")):
            os.makedirs(os.path.join(self.dest, "latest"))
        if os.path.exists(self.latest):
            os.remove(self.latest)
        if self.verbose>0:
            print _("update 'latest'...")
        os.symlink(self.rev_path, self.latest)
    def compare(self):
        if not os.path.exists(os.path.join(self.dest, "latest")):
            os.makedirs(os.path.join(self.dest, "latest"))
        if not os.path.exists(self.latest):
            self._copy_all()
        else:
            comparer=filecmp.dircmp(self.latest, self.src)
            for fn in comparer.right_only:
                self.make_copy(os.path.join(self.src, fn))
            for fn in comparer.common_funny:
                self.make_copy(os.path.join(self.src, fn))
            for fn in comparer.diff_files:
                self.make_copy(os.path.join(self.src, fn))
            for fn in comparer.same_files:
                self._make_link(os.path.join(self.latest, fn))
            for subdir_ in comparer.subdirs:
                self._compare_subdir(comparer.subdirs[subdir_], subdir_)
    def _copy_all(self):
        self._copy_dir(self.src)
    def _copy_dir(self, src_):
        dst=src_.replace(self.src, self.rev_path, 1)
        names=os.listdir(src_)
        errors = []
        for name in names:
            srcname = os.path.join(src_, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.isdir(srcname):
                    os.makedirs(dstname)
                    self._copy_dir(srcname)
                else:
                    self.make_copy(srcname)
            except (IOError, os.error), why:
                errors.append((srcname, dstname, why))
        if errors:
            raise Error, errors
    def _is_internal_link(self, path):
        """Check Symlink is linked to internal of src tree"""
        if os.path.islink(path):
            linkto=os.readlink(path)
            if os.path.commonprefix([self.src,
                                     os.path.abspath(linkto)])==self.src:
                return 1
            else:
                return 0
        else:
            return 0
    def _compare_subdir(self, subdircmp, subdirpath):
        for fn in subdircmp.right_only:
            self.make_copy(os.path.join(self.src, subdirpath, fn))
        for fn in subdircmp.common_funny:
            self.make_copy(os.path.join(self.src, subdirpath, fn))
        for fn in subdircmp.diff_files:
            self.make_copy(os.path.join(self.src, subdirpath, fn))
        for fn in subdircmp.same_files:
            self._make_link(os.path.join(self.latest, subdirpath, fn))
        for subdir_ in subdircmp.subdirs:
            self._compare_subdir(subdircmp.subdirs[subdir_], 
                                 os.path.join(subdirpath, subdir_))
    def _exclude(self,path):
        ret=0
        for mt in self.matcher:
            ret=ret or mt.exclude(path)
        return ret
    def add_matcher(self,matcher_):
        self.matcher.append(matcher_)
    def _regist_hash(self,path):
        _hash=sha.new(file(path,"r").read())
        _digest=_hash.digest()
        try:
            tmp=self.hash_db[_digest]
        except KeyError:
            tmp=[]
        if tmp:
            tmp.append(path)
        else:
            tmp=[path]
        self.hash_db[_digest]=tmp
    def _find_hash(self,path):
        _hash=sha.new(file(path,"r").read())
        _digest=_hash.digest()
        try:
            tmp=self.hash_db[_digest]
        except KeyError:
            tmp=[]
        ret=[]
        for fn in tmp:
            if os.path.exists(fn):
                ret.append(fn)
        if ret:
            self.hash_db[_digest]=ret
            return ret[0]
        else:
            return None


import sys
from optparse import OptionParser
if __name__ == '__main__':
    usage="%prog [options] src dest\n"+\
        _("BackUp solution like pseudo plan9's dumpfs")
    parser=OptionParser(usage=usage,version=u"%prog 1.0.4 by HASEGAWA Masahiro<hasegawa@mapse.eng.osaka-u.ac.jp>")
    parser.set_defaults(verbose=0)
    parser.set_defaults(dryrun=False)
    parser.add_option("-e","--exclude",dest="exclude_expr",action="append",
            metavar="EXPR",help=_("regular expression for exclude file"))
    parser.add_option("-s","--size",dest="exclude_size",action="append"
            ,metavar="NUM[GMk]",help=_("max limit of file size"))
    parser.add_option("-v","--verbose", action="store_const",const=1,
            dest="verbose",help=_("detailed output"))
    parser.add_option("-q","--quiet", action="store_const", const=0,
            dest="verbose",help=_("become taciturn"))
    parser.add_option("-n","--dry-run",action="store_true",dest="dryrun",
            help=_("do nothing, output only"))
    parser.add_option("-d","--debug",action="store_const", const=2,
            dest="verbose",help=_("most detailed output"))
    (options, args) = parser.parse_args()
    if len(args) < 2 :
        print _("need more 2 arguments")
        parser.parse_args(["-h"])
        sys.exit(2)
    else:
        dumpfs=pdumpfs(args[0],args[1],options.verbose)
        if options.verbose>0:
            print _("Backup From:"),dumpfs.src
            print _("Backup To:"),dumpfs.dest
            print _("List of regular expression of exclude file name:")
            print options.exclude_expr
            maxsize=0
            if options.exclude_size:
                maxsize=SizeMatcher("1").calc_size(options.exclude_size[0])
                for x in options.exclude_size[1:]:
                    if maxsize > SizeMatcher("1").calc_size(x):
                        maxsize=SizeMatcher("1").calc_size(x)
            psize="%s"%maxsize
            if maxsize>=1024*1024*1024:
                psize="%sGB"%(maxsize/(1024*1024*1024))
            elif maxsize>=1024*1024:
                psize="%sMB"%(maxsize/(1024*1024))
            elif maxsize>=1024:
                psize="%skB"%(maxsize/1024)
            print _("Max size of file:"),"\t%sB ( %s )"%(maxsize,psize)
        if options.exclude_expr:
            for x in options.exclude_expr:
                dumpfs.add_matcher(NameMatcher(x))
        if options.exclude_size:
            for x in options.exclude_size:
                dumpfs.add_matcher(SizeMatcher(x))
        if not options.dryrun:
            dumpfs.make_rev_path()
            dumpfs.compare()
            dumpfs.update_latest_link()
