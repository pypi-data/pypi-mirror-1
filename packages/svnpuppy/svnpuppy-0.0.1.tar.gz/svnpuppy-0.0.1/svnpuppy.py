#!/usr/bin/env python
from subprocess import call, Popen, PIPE
from gzip import GzipFile
from bz2 import BZ2File
from logging import debug, info, warning
from os import listdir, sep, stat
from os.path import isdir, basename, isfile
from optparse import OptionParser
import sys
from time import sleep

__version__ = '0.0.1'

class SVNError(Exception):
    pass

class RepositoryNotFound(Exception):
    pass

class DestinationNotDirectory(Exception):
    pass


class ArchiveTypeNotDeclared(Exception):
    pass

class DumpSVN(object):
    arc_lookup = {'gz':'.gz', 'bz2':'.bz2'}
    def __init__(self, repo, arc_type='bz2'):
        self.repo = repo
        self.arc_type = arc_type
        

    def verify_repo(self):
        debug("Verfiying repository: %s", self.repo)
        try:
            ret = call(['svnadmin', 'verify', self.repo])
        except Exception, e:
            raise SVNError(e)
        if ret == 1:
            return False
        return True


    def dest_opener(self, filename):
        arc = self.arc_type
        if arc == 'gz':
            writer = GzipFile(filename, mode='w', compresslevel=9)
        elif arc == 'bz2':
            writer = BZ2File(filename, mode='w', compresslevel=9)
        else:
            raise ArchiveTypeNotDeclared()
        return writer    


    def dest_close(self, writer):
        writer.close()

    def dump_repo(self, dest):
        filename = dest + self.arc_lookup[self.arc_type]
        debug("Dumping repository: %s at %s", self.repo, filename)
        try:
            proc = Popen(['svnadmin', 'dump', self.repo], stdout=PIPE)
        except Exception, e:
            raise SVNError(e)
        std_dump = proc.communicate()[0]
        writer = self.dest_opener(filename)
        writer.write(std_dump)
        self.dest_close(writer)
        return True







class Archive(object):
    def __init__(self, src, dest, arc_type, incCount=0):
        self.src = src
        self.dest = dest
        self.arc_type = arc_type 
        self.incCount = incCount

    def backup(self):
        testTopLevel = DumpSVN(self.src, self.arc_type)
        # check if source specified is a repository or toplevel directory
        # with repositories underneath
        if testTopLevel.verify_repo():
            cand_list.append(self.src)
        else:
            cand_list_temp = listdir(self.src)
            cand_list = []
            for fileobj in cand_list_temp:
                cand_list.append(self.src + sep + fileobj)

        check_list = []
        for fileobj in cand_list:
            if isdir(fileobj):
                check_list.append(fileobj)
        if isdir(self.dest) != True:
            raise DestinationNotDirectory()
        success_fail_dict= {}
        for repo in check_list:
            src_filename = self.src + sep + basename(repo)
            svn_instance = DumpSVN(src_filename, self.arc_type)
            if svn_instance.verify_repo() == False:
                ret = False
                continue
            try:
                dest_filename = self.incremental(basename(repo), self.dest, 
                                             self.incCount, self.arc_type)
                debug("Dumping at %s" % dest_filename)
                ret = svn_instance.dump_repo(dest_filename)
            except Exception, e:
                debug("Failure to dump %s" % e)
            success_fail_dict[repo] = ret
        return success_fail_dict
            
    def incremental(self, repo, dest, inc, arc_type):
        if self.incCount == 0:
            return dest + sep + repo + '.dump'
        else:
            incFiles =  []
            for id in range(0, inc):
                fname = dest + sep + repo + '.dump.' + str(id)
                arc = DumpSVN.arc_lookup[arc_type]
                if isfile(fname+arc) == False:
                    fd = open (fname+arc, 'w')
                    sleep(1)
                    fd.close()
                statinfo = stat(fname+arc)[9]

                incFiles.append((statinfo,fname))
            incFiles.sort()
            return incFiles[0][1]
                



if __name__ == '__main__':
    parser = OptionParser(usage="%prog -R <src repository> -B <backup destination>" )
    parser.add_option('-R', '--repository', dest="src",
                      help="Top level directory containing SVN repositories", default='/var/lib/svn')
    parser.add_option('-B', '--backup-directory/file', dest='dest', 
                      help="Top level directory under which backup will be stored", default='/var/backups/svn')
    parser.add_option('-c',  "--compress", dest='compress', default="bz2")
    parser.add_option('-I', "--incremental", dest='inc', type='int', 
                      default = 0 , help = "Increments value for incremental backup")
    (options, args) = parser.parse_args()
    ar = Archive(options.src, options.dest, options.compress, options.inc)
    
