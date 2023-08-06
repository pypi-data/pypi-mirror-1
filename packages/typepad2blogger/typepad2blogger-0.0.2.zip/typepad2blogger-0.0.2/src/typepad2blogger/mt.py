""" mt - moveable type module
    includes base error and base object
"""
from __future__ import generators

__version__ = "0.0.1"
__all__ = ['MoveableTypeError','MoveableType','blog',
           'entry','body','extendedbody','excerpt',
           'keywords','ping','comment','metadata',
           'stringdata']

class MoveableTypeError(Exception):
    """ Error to throw when dealing with mt """
    pass

class MoveableType(object):
    """ Base class so we can ask if object is a MoveableType object """
    pass

# um. don't ever try to inherit and extend the immutable types str or unicode.

class stringdata(MoveableType):
    """ base class for multiline string data fields """
    # override __delimiter__ in your implementation class.
    __delimiter__ = None
    def __init__(self,input=None):
        if isinstance(input,basestring):
            self.__data = unicode(input.strip("\r\n-").replace("\r\n","\n"))
            if self.__data.startswith(unicode(self.__delimiter__)):
                self.__data = self.__data[len(self.__delimiter__) + 1:]
                if len(self.__data):
                    self.__data += "\n"
                else:
                    raise ValueError("Empty %s entry." % self.__delimiter__)
            else:
                raise MoveableTypeError("first line of delimited input must start with '%'" % self.__delimiter__)
        else:
            raise TypeError("input must be a 'basestring' type object: " + \
                            "got %s type" % str(type(input))[6:-1])
            
    def __unicode__(self):
        """ returns self.__data as string with default unicode() encoding """
        if len(self.__data):
            return unicode(self.__data)
        else:
            raise MoveableTypeError

    def __str__(self):
        """ returns self.__data as string """
        if len(self.__data):
            return str(self.__data)
        else:
            raise MoveableTypeError

# could make a dictdata for dicty types?
    
class body(stringdata):
    """ The body of the entry. """
    __delimiter__ = u"BODY:"
    def __init__(self,input=None):
        stringdata.__init__(self,input)

class extendedbody(stringdata):
    """ The extended body of the entry. """
    __delimiter__ = u"EXTENDED BODY:"
    def __init__(self,input=None):
        stringdata.__init__(self,input)

class excerpt(stringdata):
    """ The excerpt of the entry. """
    __delimiter__ = u"EXCERPT:"
    def __init__(self,input=None):
        stringdata.__init__(self,input)

# Ok. So, apparently the KEYWORDS: tag is defined and everyone uses it,
# but there's no fucking documentation on it.
# It was used by everyone for something different:
# 0. A place to store metadata or keywords. 
#     http://forums.sixapart.com/index.php?showtopic=15500&mode=linear
# 1. a place to store temp data for plugin hacks
#     http://www.erikjheels.com/?p=558
# 2. a place to store tags, before there was a tags feature.
#     http://www.learningmovabletype.com/a/001578keywords_to_tags/
#
# We'll just handle it as string data,
# deleting the keyword: line, and storing the rest.
# maybe users will write handlers for what to do with their keywords.

class keywords(stringdata):
    """ The keywords of an entry. """
    __delimiter__ = "KEYWORDS:"
    def __init__(self,input=None):
        stringdata.__init__(self, input)
                
class ping(MoveableType, dict):
    """
    Represents one TrackBack ping on an entry. 
    Multiple PING sections can appear

    * TITLE
      The title of this ping.
    * URL
      The URL to the original entry.
    * IP
      The IP address of the server that sent the ping.
    * BLOG NAME
      The name of the weblog from which the ping was sent.
    * DATE
      The date on which the ping was sent.
    * EXCERPT
      Any line that does not match one of the above keys 
      starts the multi-line EXCERPT.
    """
    
    def __init__(self,input=None):
        dict.__init__(self)
        if isinstance(input,basestring):
            #if not input.startswith('PING:'):
            #    raise MoveableTypeError
            lines = input.strip("\r\n-").replace("\r\n","\n").split("\n")
            for line in lines:
                if 'EXCERPT' in self.keys():
                    self['EXCERPT'].append(line)
                else:
                    if line.startswith('PING:'):    continue
                    elif line == ('-----'):         continue
                    elif line.startswith('TITLE:')  or \
                         line.startswith('URL:')    or \
                         line.startswith('IP:')     or \
                         line.startswith('DATE:')   or \
                         line.startswith('BLOG NAME:'):
                            k,v = line.split(':',1)
                            self[k] = v.strip()
                    else:
                        self['EXCERPT'] = [line]
            if 'EXCERPT' in self.keys():
                if self['EXCERPT'][-1] == '-----':
                    self['EXCERPT'].pop()
            self['EXCERPT'] = unicode("\n".join(self['EXCERPT'])+"\n")  
        else:
            raise TypeError("input must be a 'basestring' type object: " + \
                            "got %s type" % str(type(input))[6:-1])

class comment(MoveableType, dict):
    """
    Represents one comment on this entry. 
    Multiple COMMENT sections can appear.

    * AUTHOR
      The name of the author of the comment.
    * EMAIL
      The email address of the author of the comment.
    * URL
      The URL of the author of the comment.
    * IP
      The IP Address of the author of the comment.
    * DATE
      The date on which the comment was posted.
    * BODY
      Any line that does not match one of the above keys 
      starts the multi-line BODY of the comment.
    """
    
    def __init__(self,input=None):
        dict.__init__(self)
        if isinstance(input,basestring):
            #if not input.startswith('COMMENT:'):
            #    raise MoveableTypeError
            lines = input.strip("\r\n-").replace("\r\n","\n").split("\n")
            for line in lines:
                if 'BODY' in self.keys():
                    self['BODY'].append(line)
                else:
                    if line.startswith('COMMENT:'):    continue
                    elif line == ('-----'):         continue
                    elif line.startswith('AUTHOR:')  or \
                         line.startswith('EMAIL:')    or \
                         line.startswith('URL:')    or \
                         line.startswith('IP:')     or \
                         line.startswith('DATE:'):
                            k,v = line.split(':',1)
                            self[k] = v.strip()
                    else:
                        self['BODY'] = [line]
            if 'BODY' in self.keys():
                if self['BODY'][-1] == '-----':
                    self['BODY'].pop()
            self['BODY'] = unicode("\n".join(self['BODY']) + "\n")  
        else:
            raise TypeError("input must be a 'basestring' type object: " + \
                            "got %s type" % str(type(input))[6:-1])

class metadata(MoveableType, dict):
    """
    # AUTHOR
    The author of the entry.
    If importing data and author is undefined, 
    become the logged in author.
    # TITLE
    The title of the entry. 
    If not assigned, first 5 words of body become title.
    # DATE (required)
    The authored-on date of the entry.
    # PRIMARY CATEGORY
    The primary category to which the entry is assigned.
    If not assigned, and CATEGORY is assigned, first CATEGORY becomes primary.
    # CATEGORY
    A list of secondary categories to which the entry is assigned.
    # STATUS
    The post status of the entry. 
    Valid values are either draft or publish.
    # ALLOW COMMENTS
    The value for the ``allow comments'' flag for the entry. 
    Valid values are either 0 or 1.
    # ALLOW PINGS
    The value for the ``allow pings'' flag for the entry.
    Valid values are either 0 or 1.
    # CONVERT BREAKS
    The value for the ``convert breaks'' flag for the entry. 
    Valid values are either 0 or 1.
    # NO ENTRY
    A special key used when importing data from a system 
    where you have already imported all of the entries, 
    but not the comments. 
    
    If you use this, the DATE key is required, 
    and will be used to look up the entries 
    with which the comments are associated; 
    if a matching entry cannot be found by 
    matching the timestamps, the comments 
    will be skipped. 
    You probably don't need to use this.
    """
    
    def __init__(self,input=None):
        dict.__init__(self)
        if isinstance(input,basestring):
            # remove garbage chars that create empty array items,
            # flip win32 newlines to raw \n, and then split into lines on \n
            lines = input.strip("\n-").replace("\r\n","\n").split("\n")
            for line in lines:
                if line.startswith('AUTHOR:')           or \
                   line.startswith('TITLE:')            or \
                   line.startswith('DATE:')             or \
                   line.startswith('PRIMARY CATEGORY:') or \
                   line.startswith('STATUS:'):
                        k,v = line.split(':',1)
                        self[k] = v.strip()
                elif line.startswith('CATEGORY:'):
                    k,v = line.split(':',1)
                    if not k in self.keys():
                        self[k] = list()
                    self[k].append(v.strip())
                elif line.startswith('ALLOW COMMENTS:') or \
                     line.startswith('ALLOW PINGS:')    or \
                     line.startswith('CONVERT BREAKS:') or \
                     line.startswith('NO ENTRY:'):
                        k,v = line.split(':',1)
                        self[k] = bool(v.strip())
                elif line.strip() == "":
                    # skip whitespace-only lines
                    continue
                else:
                    raise MoveableTypeError
                                    
        else:
            raise TypeError("input must be a 'basestring' type object: " + \
                            "got %s type" % str(type(input))[6:-1])

class entry(MoveableType):
    def __init__(self, input=None):
        if isinstance(input,basestring):
            separator = '-----\n'
            # do we lose the last newline of the second-to-last entry
            # if --------\n came with us?
            fields = input.strip("\r\n-").replace("\r\n","\n").split(separator)
            for field in fields:
                # be nice if this was a loop over the keywords...
                if field.startswith('BODY:'):
                    if not hasattr(self,'body'):
                        try:
                            self.body = body(field)
                        except ValueError, e:
                            self.body = None
                    else:
                        raise MoveableTypeError
                elif field.startswith('EXTENDED BODY:'):
                    if not hasattr(self,'extendedbody'):
                        try:
                            self.extendedbody = extendedbody(field)
                        except ValueError, e:
                            self.extendedbody = None
                    else:
                        raise MoveableTypeError
                elif field.startswith('EXCERPT:'):
                    if not hasattr(self,'excerpt'):
                        try:
                            self.excerpt = excerpt(field)
                        except ValueError, e:
                            self.excerpt = None
                    else:
                        raise MoveableTypeError
                elif field.startswith('KEYWORDS:'):
                    if not hasattr(self,'keywords'):
                        try:
                            self.keywords = keywords(field)
                        except ValueError, e:
                            self.keywords = None
                    else:
                        raise MoveableTypeError
                elif field.startswith('COMMENT:'):
                    if not hasattr(self,'comments'):
                        self.comments = list()
                    try:
                        self.comments.append(comment(field))
                    except ValueError, e:
                        pass
                elif field.startswith('PING:'):
                    if not hasattr(self,'pings'):
                        self.pings = list()
                    try:
                        self.pings.append(ping(field))
                    except ValueError, e:
                        pass
                elif field.strip() == "":
                    continue
                else:
                    if not hasattr(self,'metadata'):
                        self.metadata = metadata(field)
                    else:
                        raise MoveableTypeError

class blog(MoveableType,list):
    """ mt.blog - moveable type list container object for entry objects
    
    http://www.typepad.com/t/app/weblog/post?__mode=export&blog_id=1608662
    files are exported into the moveable type export / import format.
    http://www.sixapart.com/movabletype/docs/mtimport.html
    """

    def __init__(self,input=None):
        # at some point,
        # test adding of mt lists together
        # and handling other non MoveableType
        # sequences. 
        if input:
            for entry in self.read(input):
                try:
                    self.append(self.deserialize(entry))
                except Exception, e:
                    raise e

    def read(self,input,blocksize=8192):
        """ Based on:
            http://mail.python.org/pipermail/python-list/2003-February/188538.html
        """
        import os.path
        from tempfile import TemporaryFile
        
        separator = '--------\n'
        if isinstance(input,basestring):
            if os.path.isfile(input):
                fh = open(input,'rb')
            else:
                fh = TemporaryFile('w+b')
                fh.write(input)
        elif isinstance(input,file):
            fh = input
        else:
            raise TypeError("input requires a 'file' type object or a " + \
                            "'basestring' type object: " + \
                            "got %s type" % str(type(input))[6:-1])
        fh.seek(0)
        # first chunk in
        # what happens when first block is all done?
        block = fh.read(blocksize).replace("\r\n","\n")
        while block:
            index = block.find(separator)
            if index < 0:
                moredata = fh.read(blocksize)
                if moredata:
                    block += moredata
                    continue
                yield block
                return
    
            index += len(separator)
            yield block[:index]
            block = block[index:]

    def deserialize(self,input):
        """ This is probably redundant, but it reads nicely. """ 
        return entry(input)
