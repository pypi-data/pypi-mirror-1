#!/usr/bin/python
# -*- coding: utf8 -*-
import sys
import os
import time
import shutil
import math
import filecmp
import re
__author__ = "HASEGAWA Masahiro <hasegawa@mapse.eng.osaka-u.ac.jp>"
__version__ = "1.0.3"
__copyright__ = "Copyright (c) 2007-2008 MASA.H"
__license__ = "New-style BSD"

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
    def _make_link(self, path):
        if self.verbose>1:
            print "ハードリンク生成:%s"%path
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
                print "シンボリックリンク生成:%s"%path
            os.symlink(linkto, path.replace(self.src, self.rev_path, 1))
    def make_copy(self, path):
        if self._exclude(path):
            if self.vaerbose>0:
                print "除外ファイル:%s"%path
        elif self._is_internal_link(path):
            self._copy_symlink(path)
        elif os.path.isdir(path):
            self._copy_dir(path)
        else:
            if self.verbose>1:
                print "コピー:%s"%path
            dst=path.replace(self.src, self.rev_path, 1)
            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            shutil.copy2(path, dst)
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
            print "ディレクトリ生成:%s"%self.rev_path
        os.makedirs(self.rev_path)
        self.tmp_path=os.path.join(self.dest, 
                            time.strftime("%Y", time.localtime(self.ntime)), 
                            time.strftime("%m", time.localtime(self.ntime)), 
                            time.strftime("%d", time.localtime(self.ntime)))
        if not os.path.exists(self.tmp_path):
            if self.verbose>0:
                print "ディレクトリ生成:%s"%self.tmp_path
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
            print "latestの更新..."
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
                # XXX What about devices, sockets etc.?
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

import unittest

class UnitTestPDumpFS(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("/data1/hasegawa/tmp/src"):
            os.makedirs("/data1/hasegawa/tmp/src")
            os.makedirs("/data1/hasegawa/tmp/src/subdir1/a")
            os.makedirs("/data1/hasegawa/tmp/src/subdir1/b")
            os.mknod("/data1/hasegawa/tmp/src/testfile")
            os.symlink("/data1/hasegawa/tmp/src/testfile","/data1/hasegawa/tmp/src/subdir1/a/test")
            os.symlink("/data1/hasegawa/.bashrc","/data1/hasegawa/tmp/src/subdir1/b/bashrc")
        self.dumpfs=pdumpfs("/data1/hasegawa/tmp/src",
                                 "/data1/hasegawa/tmp/dest")
    def test_make_path(self):
        self.dumpfs.make_rev_path()
        print time.localtime(time.time())
        print self.dumpfs.rev_path
        self.assert_(os.path.exists(self.dumpfs.rev_path))
        self.assert_(os.path.isdir(self.dumpfs.rev_path))
        print self.dumpfs.tmp_path
        self.assert_(os.path.exists(self.dumpfs.tmp_path))
        self.assert_(os.path.isdir(self.dumpfs.tmp_path))
        print self.dumpfs.tmp_path2
        self.assert_(os.path.exists(self.dumpfs.tmp_path2))
        self.assert_(os.path.islink(self.dumpfs.tmp_path2))
        self.dumpfs.compare()
        self.dumpfs.update_latest_link()
        self.assert_(os.path.exists(self.dumpfs.latest))
        self.assert_(os.path.isdir(self.dumpfs.latest))

import sys
from optparse import OptionParser
if __name__ == '__main__':
    #unittest.main()
    usage="使用方法: %prog [options] src dest\nplan9のdumpfsまがいのバックアップ作成"
    parser=OptionParser(usage=usage,version="%prog 1.0.3 by HASEGAWA Masahiro<hasegawa@mapse.eng.osaka-u.ac.jp>")
    parser.set_defaults(verbose=0)
    parser.set_defaults(dryrun=False)
    parser.add_option("-e","--exclude",dest="exclude_expr",action="append",
            metavar="EXPR",help="除外するファイル名の正規表現")
    parser.add_option("-s","--size",dest="exclude_size",action="append",metavar="NUM[GMk]",help="ファイルサイズの上限")
    parser.add_option("-v","--verbose", action="store_const",const=1, dest="verbose",help="冗長な出力をする")
    parser.add_option("-q","--quiet", action="store_const", const=0, dest="verbose",help="極力出力しない")
    parser.add_option("-n","--dry-run",action="store_true",dest="dryrun",help="実際の処理はしない")
    parser.add_option("-d","--debug",action="store_const", const=2, dest="verbose",help="非常に冗長な出力をする")
    (options, args) = parser.parse_args()
    if len(args) < 2 :
        print "%s には最低2つの引数が必要"%sys.argv[0]
        parser.parse_args(["-h"])
        sys.exit(2)
    else:
        dumpfs=pdumpfs(args[0],args[1],options.verbose)
        if options.verbose>0:
            print "バックアップ元:",dumpfs.src
            print "バックアップ先:",dumpfs.dest
            print "除外するファイル名の正規表現のリスト:"
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
            print "ファイルサイズ上限:\t%sB ( %s )"%(maxsize,psize)
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
                                           
