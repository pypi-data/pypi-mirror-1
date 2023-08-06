This package designed to find and manage duplications,
and contains two utilities:

 * dupfind - to find duplications
 * dupmanage - to manage found duplications


DUPFIND UTILITY:
================

*dupfind* utility allows you to find duplicated files and directories
in your file system.

Show how utility find duplicated files:
=======================================

By default utility identifies *duplication files* by
file content.

First of all - create several different files
in the current directory.

    >>> createFile('tfile1.txt', "A"*10)
    >>> createFile('tfile2.txt', "A"*1025)
    >>> createFile('tfile3.txt', "A"*2048)

Then create other files in another directory, one
of them to be the same as already created ones.

    >>> mkd("dir1")
    >>> createFile('tfile1.txt', "A"*20, "dir1")
    >>> createFile('tfile2.txt', "A"*1025, "dir1")
    >>> createFile('tfile13.txt', "A"*48, "dir1")

Look into the directories contents:

    >>> ls()
    === list directory ===
    D :: dir1 :: ...
    F :: tfile1.txt :: 10
    F :: tfile2.txt :: 1025
    F :: tfile3.txt :: 2048

    >>> ls("dir1")
    === list dir1 directory ===
    F :: tfile1.txt :: 20
    F :: tfile13.txt :: 48
    F :: tfile2.txt :: 1025


We see, that "tfile2.txt" is same in both directories,
while "tfile1.txt" - has the same name, but differs in size.
So utility must identify only "tfile2.txt" as a duplication file.

We force output results with "-o <output file name>"
argument to *outputf* file, and pass *testdir* as directory
that is looking for duplications.

    >>> dupfind("-o %(o)s %(dir)s" % {'o':outputf, 'dir': testdir})


Now check the results file for duplications.
 
    >>> cat(outputf)
    hash,size,type,ext,name,directory,modification,operation,operation_data
    ...,1025,F,txt,tfile2.txt,.../tmp.../dir1,...
    ...,1025,F,txt,tfile2.txt,.../tmp...,...



Show quick/slow utility mode:
=============================

As mentioned above - utility identifies *duplication files*
by file contents. This mode slows down the system and consumes
a lot of system resources.

However, in most cases the file name and size is enough to identify the
duplication. So in that case you can use *quick* mode
--quick (-q) option.

So test the previous files in the quick mode:

    >>> dupfind("-q -o %(o)s %(dir)s" % {'o':outputf, 'dir': testdir})


Now check the result file for duplications.

    >>> cat(outputf)
    hash,size,type,ext,name,directory,modification,operation,operation_data
    ...,1025,F,txt,tfile2.txt,.../tmp.../dir1,...
    ...,1025,F,txt,tfile2.txt,.../tmp...,...


As we can see the quick mode identifies duplications correctly.


Let's show that there are cases when this mode can lead to mistakes.
To do that let's add a file with the same name and size but different content
and apply utility in both modes:


    >>> createFile('tfile000.txt', "First  "*20,)
    >>> createFile('tfile000.txt', "Second "*20, "dir1")


Now check the duplication results using default (not quick mode) ...


    >>> dupfind(" -o %(o)s %(dir)s" % {'o':outputf, 'dir': testdir})
    >>> cat(outputf)
    hash,size,type,ext,name,directory,modification,operation,operation_data
    ...,1025,F,txt,tfile2.txt,.../tmp.../dir1,...
    ...,1025,F,txt,tfile2.txt,.../tmp...,...


As we can see *not-quick* mode identifies duplications correctly.

Let's check duplications using the quick mode...


    >>> dupfind(" -q -o %(o)s %(dir)s" % {'o':outputf, 'dir': testdir})
    >>> cat(outputf)
    hash,size,type,ext,name,directory,modification,operation,operation_data
    ...,140,F,txt,tfile000.txt,.../tmp.../dir1,...
    ...,140,F,txt,tfile000.txt,.../tmp...,...
    ...,1025,F,txt,tfile2.txt,.../tmp.../dir1,...
    ...,1025,F,txt,tfile2.txt,.../tmp...,...


As we can see wrong duplications are found using the quick-mode.


Cleanup the test

    >>> cleanTestDir()


Show how utility finds duplicated directories:
==============================================

Utility identifies *duplicated directories* as
directories, all files of which are *duplicated*
and all inner directories are also *duplicated
directories*.


First compare 2 directories with the same files.
------------------------------------------------

Create directories with the same content.

    >>> def mkDir(dpath):
    ...     mkd(dpath)
    ...     createFile('tfile1.txt', "A"*10, dpath)
    ...     createFile('tfile2.txt', "A"*1025, dpath)
    ...     createFile('tfile3.txt', "A"*2048, dpath)
    ... 
    >>> mkDir("dir1")
    >>> mkDir("dir2")

Confirm that the directories' contents are really identical

    >>> ls("dir1")
    === list dir1 directory ===
    F :: tfile1.txt :: 10
    F :: tfile2.txt :: 1025
    F :: tfile3.txt :: 2048

    >>> ls("dir2")
    === list dir2 directory ===
    F :: tfile1.txt :: 10
    F :: tfile2.txt :: 1025
    F :: tfile3.txt :: 2048


Now run the utility and check the result file:

    >>> dupfind("-o %(o)s %(dir)s" % {'o':outputf, 'dir': testdir})
    >>> cat(outputf)
    hash,size,type,ext,name,directory,modification,operation,operation_data
    ...,D,,dir1,...
    ...,D,,dir2,...

    
Compare 2 directories with the same files and dirs.
---------------------------------------------------

Create new directories with the same content, but different names in previously
created directories. 

So for directories to be interpreted as duplications - they don't need to have
the same name, but the identical content.

Add 2 identical directories to the previous ones.

    >>> def mkDir1(dpath):
    ...     mkd(dpath)
    ...     createFile('tfile11.txt', "B"*4000, dpath)
    ...     createFile('tfile12.txt', "B"*222, dpath)
    ... 
    >>> mkDir1("dir1/dir11")
    >>> mkDir1("dir2/dir21")

Note that we added two directories with same contents,
but different names. This should not break duplications.

    >>> def mkDir2(dpath):
    ...     mkd(dpath)
    ...     createFile('tfile21.txt', "C"*4096, dpath)
    ...     createFile('tfile22.txt', "C"*123, dpath)
    ...     createFile('tfile23.txt', "C"*444, dpath)
    ...     createFile('tfile24.txt', "C"*555, dpath)
    ... 
    >>> mkDir2("dir1/dir22")
    >>> mkDir2("dir2/dir22")


Confirm that directories' contents are really identical

    >>> ls("dir1")
    === list dir1 directory ===
    D :: dir11 :: -1
    D :: dir22 :: -1
    F :: tfile1.txt :: 10
    F :: tfile2.txt :: 1025
    F :: tfile3.txt :: 2048
    >>> ls("dir2")
    === list dir2 directory ===
    D :: dir21 :: -1
    D :: dir22 :: -1
    F :: tfile1.txt :: 10
    F :: tfile2.txt :: 1025
    F :: tfile3.txt :: 2048

And contents for inner directories

First subdirectory:

    >>> ls("dir1/dir11")
    === list dir1/dir11 directory ===
    F :: tfile11.txt :: 4000
    F :: tfile12.txt :: 222
    >>> ls("dir2/dir21")
    === list dir2/dir21 directory ===
    F :: tfile11.txt :: 4000
    F :: tfile12.txt :: 222

Second subdirectory:

    >>> ls("dir1/dir22")
    === list dir1/dir22 directory ===
    F :: tfile21.txt :: 4096
    F :: tfile22.txt :: 123
    F :: tfile23.txt :: 444
    F :: tfile24.txt :: 555
    >>> ls("dir2/dir22")
    === list dir2/dir22 directory ===
    F :: tfile21.txt :: 4096
    F :: tfile22.txt :: 123
    F :: tfile23.txt :: 444
    F :: tfile24.txt :: 555


Now test the utility.

    >>> dupfind("-o %(o)s %(dir)s" % {'o':outputf, 'dir': testdir})


Checks the results file for duplications.

    >>> cat(outputf)
    hash,size,type,ext,name,directory,modification,operation,operation_data
    ...,D,,dir1,...
    ...,D,,dir2,...


NOTE:
-----
Inner duplication directories are excluded from the results:

    >>> outputres = file(outputf).read()
    >>> "dir1/dir11" in outputres
    False
    >>> "dir1/dir22" in outputres
    False
    >>> "dir2/dir21" in outputres
    False
    >>> "dir2/dir22" in outputres
    False


Utility accepts more than one argument as directories list:
===========================================================

Use previous directory structure to prove this:

Now pass to utility "dir1/dir11" and "dir2" directories:

    >>> dupfind("-o %(o)s %(dir1-11)s %(dir2)s" % {
    ...     'o':outputf,
    ...     'dir1-11': os.path.join(testdir,"dir1/dir11"),
    ...     'dir2': os.path.join(testdir,"dir2"),})


Now check the result file for duplications.

    >>> cat(outputf)
    hash,size,type,ext,name,directory,modification,operation,operation_data
    ...,D,,dir11,.../tmp.../dir1,...
    ...,D,,dir21,.../tmp.../dir2,...



DUPMANAGE UTILITY:
==================


*dupmanage* utility allows you to manage duplication files and directories
of your file system with csv data file.

Utility use csv-formatted data-file to process duplication items.
Data file must contain the following columns:

  * type
  * name
  * directory
  * operation
  * operation_data


Utility supports 2 types of operations with duplication items:

  * deleting ("D")
  * symlinking ("L") only for UNIX-like systems

*operation_data* is only used for *symlinking* operation and 
must contain the path to symlinking sorce item.



Show how utility manages duplications:
======================================

To show - use previous directory structure and 
also add several duplications:

Create a file in the root directory and the same file
in another catalog.

    >>> createFile('tfile03.txt', "D"*100)
    >>> mkd("dir3")
    >>> createFile('tfile03.txt', "D"*100, "dir3")

Look into directories contents:

    >>> ls()
    === list directory ===
    D :: dir1 :: ...
    D :: dir2 :: ...
    D :: dir3 :: ...
    F :: tfile03.txt :: 100

    >>> ls("dir3")
    === list dir3 directory ===
    F :: tfile03.txt :: 100


We already know the previous duplications, so now we create
csv-formatted data file to manage duplications.

    >>> manage_data = """type,name,directory,operation,operation_data
    ... F,tfile03.txt,%(testdir)s/dir3,L,%(testdir)s/tfile03.txt
    ... D,dir2,%(testdir)s,D,
    ... """ % {'testdir': testdir}
    >>> createFile('manage.csv', manage_data)



Now call the utility and check result directory content:

    >>> manage_path = os.path.join(testdir, 'manage.csv')
    >>> dupmanage("%s -v" % manage_path)
    [...                                                                           
    [...]: Symlink .../tfile03.txt item to .../dir3/tfile03.txt
    [...]: Remove .../dir2 directory                                            
    [...]: Processed 2 items                                                                                                                               


Review directory content:

    >>> ls()
    === list directory ===
    D :: dir1 :: ...
    D :: dir3 :: ...
    F :: tfile03.txt :: 100

    >>> ls("dir3")
    === list dir3 directory ===
    L :: tfile03.txt :: ...

