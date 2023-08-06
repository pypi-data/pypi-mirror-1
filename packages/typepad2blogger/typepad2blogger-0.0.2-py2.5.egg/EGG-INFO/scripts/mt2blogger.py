""" scripts/mt2blogger.py

    Given a flat file in the old moveable type (mt) 
    import/export format and some blogger blog login details,
    post each mt entry to blogger blog as a draft entry.
    
    tested functional with test/data/typepad.export.data
"""

from typepad2blogger import mt, blogger
from optparse import OptionParser
import sys

usage = """\
%prog [options] email password blogname filename
  * email: your blogger username (e-mail address)
  * password: your blogger password
  * blogname: your blogger blog to import into
  * filename: your typepad export file
""" + "\n".join(__doc__.split("\n")[1:5])

def main():
    parser = OptionParser(usage=usage,version="%prog " + str(mt.__version__))
    parser.add_option("-p", "--publish", action="store_false", 
                      dest="draft", default=True,
                      help="publish imported posts immediately")
    (options, args) = parser.parse_args()
    if len(args) != 4:
        parser.print_help()
        sys.exit(1)
    (email,password,blogname,filename) = args
    
    source_blog = mt.blog(filename)
    dest_blog = blogger.blog(email,password,blogname)
    dest_blog.connect()
    
    for post in source_blog:
         # incoming blog post publish dates look like this.
         # 2008-05-16T21:50:00.001-07:00
         # but the MT dates look like this. 
         # 01/31/2002 03:31:05 PM
         date,time,ampm = post.metadata['DATE'].split()
         month,day,year = date.split('/')
         dest_date = '-'.join([year,month,day])
         if ampm == "PM":
             hour,minute,second = time.split(':')
             if int(hour) < 12:
                 h = 12 + int(hour)
                 hour = str(h)
         # yes, I hard coded the timezone to chicago CST.
         dest_time = ':'.join([hour,minute,second]) + '.001-07:00'
         dest_publishdate = 'T'.join([dest_date,dest_time]) 
             
         entry = blogger.entry(post.metadata['TITLE'],
                           unicode(post.body),
                           post.metadata['AUTHOR'],
                           dest_publishdate)
         entry_data = dest_blog.post(entry,options.draft)
         if hasattr(post,"comments"):
             for comment in post.comments:
                 # it has an ID somewhere, no? handle the comments using that.
                 # need a blog.comment() method,
                 # and a working comment object with properties for posting.
                 pass
         
  

if __name__ == '__main__':
    main()
