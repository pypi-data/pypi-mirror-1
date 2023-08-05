Short module description
=========================

Module pd.find present simple way use filesystem
to search and read files on it. File system using
showed as simple as using ordinal dict::

    >>> import pd.find
    >>> f=pd.find.file.File("/etc/sysconfig")
    >>> f
    '/etc/sysconfig'
    >>> f.keys()
    ['harddisk', 'lm_sensors', 'ipw3945d~', 'syscheckerrc', 'mouse']
    >>> f['lm_sensors']
    '/etc/sysconfig/lm_sensors'
    >>> print str(f['lm_sensors'])
    #    /etc/sysconfig/lm_sensors - Defines modules loaded by

Other important pakage mission is find files by the way similar
to command line find utility::

    >>> import pd.find
    >>> pd.find.find("/etc/sysconfig",lambda x : x.isreg() and x.check_regex(".*rc"))
    <generator object at 0xb7cca7cc>
    >>> for item in pd.find.find("/etc/sysconfig",lambda x : x.isreg() and x.check_regex(".*rc$")) : 
    ... print item.path
    ...
    /etc/sysconfig/xinitrc
    /etc/sysconfig/syscheckerrc
    >>>

Using  pd.find.file.File
--------------------------

Constructor issued as in example above, with one required
argument - path to file or directory. There are other
arguments:

    dereference 
        Follow symlinks (is False by default)
        
The File object to provide some useful methods and attributes:

    path
        Attribute present absolute file path;
        
    __str__() 
        Method returns file body if it can;
        
Other attributes do condition check and will be described bellow.

Issue pd.find.find utility
--------------------------

The pd.find.find utility issued to reqursive search files to satisfy 
some conditions. Utility accept followed arguments:

    path
        Directory path to search begin with;
        
    condition
        Condition checked on scanned files and directories. If condition satisfy - object
        yielded by utility;
    
    precondition
        Condition checked before subdirectory scan. If condition does not satisfy,
        subdirectory will not be scaned;
        
    dereference
        On true value of this argument searhing will be followed by symbolic
        link.

Utility return generator of list object find by them.

Tests provided by File Object
-----------------------------

    mtime
        Return modification time
        
    atime
        Return last access time
        
    ctime
        Return creation time """
        return self.__checktime_(stat.ST_CTIME)
        
    newer
        Return true if object is more newer then input path
    
    check_name
        Return true if object name are equal to input name

    check_path
        Return true if object path are equal to input path
        
    check_path_regex
        Return true if regexp matched object path

    check_regex
        Return true if regexp matched object name

    check_iregex
        Return true if regexp matched object name
        
    depth
        Return current depth on file tree

    dele
        Delete file by path of current object

    execute
        Frm will be substituted by substring "{}" on path and executed
        by os.system() call

Ho-ho. Sorry my English :)
    