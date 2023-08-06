#!/usr/bin/env python
"""Duplication finder utility.
Find duplication files in passed director[y/es]

%prog [options] <find_dir_1> [<find_dir_2> <find_dir_3>]
"""

import os, sys, time, csv, copy
import operator
import zlib
from cStringIO import StringIO
from optparse import OptionParser

#######################################
#         Setup logging system        #
#######################################
import logging
DEFAULT_LOG = "/tmp/dupfind.log"
FORMAT = "[%(asctime)s]: %(message)s"
#FORMAT = "[%H:%M:%S]: %(message)s"
def createHandler(hndlr_cls, level, *args, **kwargs):
    hndlr = hndlr_cls(*args, **kwargs)
    hndlr.setLevel(level)
    hndlr.setFormatter(logging.Formatter(FORMAT, datefmt="%H:%M:%S"))
    return hndlr

# Very IMPORTANT create logger as logging.Logger NOT logging.getLogger !!!
logger = logging.Logger("Copy Flash", logging.NOTSET)
logger.addHandler(createHandler(
        logging.FileHandler, logging.DEBUG, DEFAULT_LOG))

#######################################

class DupFinder(object):
    """
    """

    def __init__(self, dirs=[], quick=False):
        self.dirs = map(os.path.abspath, dirs)
        self.quick = bool(quick)
#        self.dups = []


    def find(self):
        """ Return list of duplications tuple in format:
            [(hash-key, duplication data),...]
        """
        logger.info("Prepare informations for: %s" % str(self.dirs))
        dups = []

        dirsdata = {}
        for data in [self.getPathData(dir) for dir in self.dirs]:
            dirsdata.update(data)

        logger.info("There are %d files and directories in %s" % (
                len(dirsdata), self.dirs) )

        # Reorganize data in such way to make duplications to be a neighbors
        resmap = []
        for path, pdata in dirsdata.items():
            pdata['path'] = path
            resmap.append((pdata["hash"], pdata))
        resmap.sort()

        logger.info("Filter out duplications" )

        prevh, prevd = resmap[0]
        dup = None
        for currh, currd in resmap[1:]:
            if currh == prevh:
                if dup is None:
                    dup = [ (prevh, prevd) ]
                dup.append( (currh, currd) )

            else:
                if dup is not None:
                    dups.extend(dup)
                    dup = None

            prevh, prevd = currh, currd
        # Belong to previous loop: add last duplications
        if dup is not None:
            dups.extend(dup)

        dups = self.filterInnerDups(dups)

        logger.info("Found %d duplications" % len(dups)) 
        return dups


    def getPathData(self, base_dir):
        """Generate dictionary with path as key and data for the path:
           { path1:
                { hash: int,
                  size: int,
                  type: 'F'/'D',
                  mtime: str (modification time)},
             ...
             pathN: }

        Dictionary forms from all iner directory and files for the giver base_dir

        Arguments:
        base_dir -- top level directory to generate Data for.

        """
        def getASCTime(t):
            return time.asctime(time.localtime(t))[4:]

        def hash_name_size(fname, fsize, fpath):
            return hash((fname, fsize))

        def hash_content(fname, fsize, fpath):
            if os.path.islink(fp):
                return hash(os.path.realpath(fpath))
            return hash( zlib.crc32(file(fpath,'rb').read()) )

        file_hash_fnc = self.quick and hash_name_size or hash_content
        base_dir = os.path.abspath(base_dir)
        hash_table = {}
        for dpath, dirs, files in os.walk(base_dir, topdown=False):
            dirsize = 0

            dirs_hashpart = []
            for d in dirs:
                dp = os.path.abspath(os.path.join(dpath, d))
                ddata = hash_table.get(dp, {"hash": 0, "size": 0})
                dirs_hashpart.append( (ddata["hash"], ddata["size"]) )
                dirsize += ddata["size"]

            files_hashpart = []
            for f in files:
                fp = os.path.abspath(os.path.join(dpath, f))
                try:
                    fsize = os.path.getsize(fp)
                except OSError:
                    fsize = 0
                dirsize += fsize

                try:
                    fmtime = getASCTime(os.path.getmtime(fp))
                except OSError:
                    fmtime = getASCTime(os.path.getmtime(dpath))

                filehash = file_hash_fnc(f, fsize, fp)
                files_hashpart.append( filehash )

                hash_table[fp] = {"hash": filehash, "size": fsize,
                                  "type": 'F', 'mtime': fmtime}

            dmtime = getASCTime(os.path.getmtime(dpath))
            # caculate directory hash
            dirs_hashpart.sort()
            files_hashpart.sort()
            dirhash = hash((tuple(dirs_hashpart), tuple(files_hashpart)))

            hash_table[dpath] = {"hash": dirhash, "size": dirsize,
                                 "type": 'D', 'mtime': dmtime}

        return hash_table


    def filterInnerDups(self, dups):
        """Remove inner content for duplication directories
        """
        logger.info("Remove inner content for duplication directories")
        logger.debug("Before cleaning up duplication dirs: %d" % len(dups))
        res = []

        deepdata = {}
        for hsh, ddata in dups:
            deep = len(ddata["path"].split(os.sep))
            deeplst = deepdata.setdefault(deep, [])
            if ddata["type"] == "D":
                deeplst.insert(0, ddata)
            else:
                deeplst.append(ddata)

        deeps = deepdata.keys()
        deeps.sort()
        for deep in deeps[:-1]:
            for data in deepdata[deep]:
                if data["type"] == "F":
                    break

                dpath = data["path"]
                deepindx = deeps.index(deep)
                for lowdeep in deeps[deepindx+1:]:
                    deepdata[lowdeep] = filter(
                        lambda d: not d["path"].startswith(dpath),
                        deepdata[lowdeep])

        for dups in deepdata.values():
            for d in dups:
                res.append((d["hash"], d))
        res.sort()
        logger.debug("After cleaning up duplication dirs: %d" % len(res))

        return res



class DupOut(object):
    """ Prepare and output duplications in selected format.
    """

    formats = ["CSV",]
    file = "duplications.csv"
    minSize = 0
    
    def __init__(self, format="CSV", minSize=None):
        format = format.upper()
        self.format = self.formats.index(format)>-1 and format or "CSV"
        if minSize is not None:
            self.minSize = int(minSize)
        

    def out(self, dups, outf=file):

        logger.info("Output duplications into %s, in %s format" % (outf, self.format))

        if self.minSize > 0:
            dups = self.filterBySize(dups)

        if self.format=="CSV":
            self.csvFormatter(dups, outf)

        extraSize, totalSize, files, dirs = self.getStats(dups)
        extraSizeMb, totalSizeMb = map(lambda x:x/(1024*1024), [extraSize, totalSize])

        logger.info("TOTAL duplications:%d [FILES:%d, DIRECTORIES:%d]" % (
                files+dirs, files, dirs))
        logger.info("Extra SIZE, occupated by duplications: %dMb" % extraSizeMb)
        logger.info("TOTAL SIZE, occupated by duplications: %dMb" % totalSizeMb)

    
    def filterBySize(self, dups):
        if self.minSize > 0:
            return [(h,d) for h, d in dups if d["size"] >= self.minSize]
        return dups


    def getStats(self, dups):
        prevh, prevd = dups[0]
        files, dirs = map(lambda t:prevd["type"]==t and 1 or 0, ["F","D"])
        extraSize, totalSize = 0, prevd["size"]
        for currh, currd in dups[1:]:
            f, d = map(lambda t:prevd["type"]==t and 1 or 0, ["F","D"])
            totalSize += currd["size"]
            if currh == prevh:
                extraSize += currd["size"]
            if currd["type"] == "F":
                files += 1
            else:
                dirs += 1
            prevh = currh

        return extraSize, totalSize, files, dirs


    def csvFormatter(self, data, outfile):
        """Output [data] into [outfile] in CSV format."""

        out = file(outfile, 'wb')
        fields = ['hash', 'size', 'type', 'ext', 'name', 'directory',
                  'modification', 'operation', 'operation_data']
        writer = csv.DictWriter(out, fieldnames=fields, dialect="excel")
        writer.writerow(dict(zip(fields,fields)))

        for hsh, pdata in data:
            dir, name = os.path.split(pdata["path"])
            if pdata["type"] == "F":
                ext = os.path.splitext(name)[1]
                ext = ext and ext[1:] or ext
            else:
                ext = ""
            writer.writerow(
                {'hash': hsh,
                 'size': pdata["size"],
                 'type': pdata["type"],
                 'ext': ext,
                 'name': name,
                 'directory': dir,
                 'modification': pdata["mtime"]})
            out.flush()

        out.close()



def getConsoleParams():
    parser = OptionParser(__doc__)

#    parser.add_option("-f", "--output-format", dest="output_format", default="CSV",
#        help="Output format for result. Possible formats: %s, default='%default'")
    parser.add_option("-o", "--output-file", dest="output_file", default=DupOut.file,
        help="Path to (name of) result file")
    parser.add_option("-m", "--minimal-size", dest="minSize", type="int", default=0,
        help="Set minimal size for duplications - smaler files will be filtered out, default='%default'")
    parser.add_option("-q", "--quick", dest="quick", action="store_true", default=False,
        help="Quick file comparison only by file-name and file-size. If False - " \
              "file duplication calculated by content. Default='%default'")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
        help="Show duplications to console, default='%default'")

    (options, args) = parser.parse_args()

    logger.debug("Got options: %s\narguments: %s" % (str(options), str(args)))

    try:
        dirs = args
        assert len(dirs) > 0, "At least one directory must be passed in"

#        output_format = options.output_format.upper() in DupOut.formats \
#            and options.output_format.upper() or DupOut.formats[0]
        output_format = DupOut.formats[0]
    except:
        print parser.print_help()
        raise

    return (dirs, options.minSize, options.output_file, output_format,
            options.quick, options.verbose)
    

def main(dirs=[], minSize=0, outf=DupOut.file, outformat=DupOut.formats[0],
         verbose=False):

    if not dirs:
        dirs, minSize, outf, outformat, quick, verbose = getConsoleParams()

    if verbose:
        logger.addHandler(createHandler(
                logging.StreamHandler, logging.INFO, sys.stdout))

    dups = DupFinder(dirs, quick).find()
    DupOut(format=outformat, minSize=minSize).out(dups, outf=outf)


if __name__ == '__main__':
    main()
