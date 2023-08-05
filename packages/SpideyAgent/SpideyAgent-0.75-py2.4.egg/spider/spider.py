#Core spidering module
from cPickle import *
from cStringIO import StringIO
from htmllib import HTMLParser
from formatter import DumbWriter,AbstractFormatter
from os.path import *
from os import makedirs,listdir
import re
from string import *
from thread import *
from urllib import *
from urlparse import *
from model import *
from time import *

class spider:
    def __init__(self,user):
        self.stop = False
        self.completelystopped = False
        self.VERBOSE = "On"  #unused
        self.FIND_EVERY_WORD = "On"
        self.MAX_DOWNLOAD_THREADS = 5 #0 for none unused
        self.MAX_CRAWL_THREADS = 5
        self.threads = 0
        self.RESUME = "Off"
        self.CHECK_KNOWN_SITES_FIRST = "Off"
        self.TIME_TILL_URL_FRESH =   60*60*24 #24 hours I think if in seconds not used for a long time no pickling anymore left in place for possible usage
        self.TIME_TILL_PICKLE =      60*5
        self.TIME_LAST_PICKLED =     0
        self.threadsDownloading = 0
        self.regex_FILES  = "(http://[^\"\'>]+\.mpg|\.wmv|\.avi|\.mpeg|\.rm|\.pdf)" #currently not used 
        self.siteLog = open("sitelog",'a')
        self.mediaLog = open("medialog",'a')
        self.exceptionLog = open("exceptionlog",'a')
        self.sitesWithFilesLog = open("sitesWithFileslog",'a')
        self.siteSet = {}     #every url spidered
        self.sitesWithFilesSet = {}     #sites where files were found unused
        self.files = []     #files found
        self.siteQue = []
        self.user = user
        self.userid = None
        self.userObj = None
        self.dictionaryDB = {}
        self.wordDBBuiltYet = 0
    def processWords(self,site,data):
        lines = data.splitlines()
        self.findEveryWord(site,lines)
    def pickleCheck(self):
        if (time() - self.TIME_LAST_PICKLED) > self.TIME_TILL_PICKLE :
            print '\nPickling...\n'
            ss = 'siteSet_for_'+self.user+'.pickle'
            d = 'dictionary_for_'+self.user+'.pickle'
            t = time()
            dump(self.siteSet,open(ss,'w'))
            dump(self.dictionary,open(d,'w'))
            print time()-t,'is the time taken to pickle'#,ss,d
            self.TIME_LAST_PICKLED = time()
    def findEveryWord(self,site,lines=[]):
        '''Catalog each word by url'''
        t = time()
        conpool.getConnection()
        conpool.getLock()
        con = MySQLdb.connect('localhost','root','sniggle','spiderpydb',3306)
        conpool.relLock()
        cu = con.cursor()
        words = []
        cnt = 0
        word_set =set()
        hub.begin()
        #try:
        for line in lines:
            #Remove \t from the text
            #<*.?> or <[^>]*>
            line = re.sub('<*.?>', '', line)
            line = re.sub('\t+','',line)
            allWords = re.findall('\w+',line)
            for word in allWords:
                cnt +=1
                word_set.add(word)
        selectedURI = URI.select(URI.q.address == site)
        selectedURIList = list(selectedURI)
        if len(selectedURIList) == 0:
            time_=time()
            d = str(lines)
            c = URI(address=site,data=d,time=time_)
            hub.commit()
        else:
            c = selectedURIList[0]
        sql_us = "SELECT * FROM ur_i WHERE address = '%s'" % site
        rws = cu.execute(sql_us)
        a= cu.fetchall()
        if len(a) > 0:
            uriid = a[0][0]
            address = a[0][1]
        else:
            print 'no uri found'
            raise 
        sql_us = "SELECT id,name FROM user WHERE name = '%s'" % self.user
        rws = cu.execute(sql_us)
        b = cu.fetchall()
        if len(b) > 0:
            uid = b[0][0]
            name = b[0][1]
        else:
            print 'no user found'
        cu.executemany("INSERT INTO entry (word,uri_id,user_id) VALUES (%s,%s,%s)", [(word,uriid,uid) for word in word_set ])
        #hub.end()
        #print 'total words in site',cnt,
        #print 'words in set',len(word_set)
        dt = time() - t
        #print dt, 'to find and insert all words from ',site
        cu.close()
        con.close()
    def relativeToAbsolute(self,url,links):
        '''convert a url from relative to absolute terms given a url and a list of links'''
        url = url.strip()
        if len(url) > 1:
            try:
                a = []
                for x in links:
                    x = x.strip()
                    if 'http://' not in x and 'https://' not in x:
                        #print 'link was',x
                        x = urljoin(url,x)
                        #print 'link now',x
                    a.append(x)
                return a
            except:
                print 'exception in relativetoabsolute',url,links
    def getAnchors(self,data):
        #print '''Given a file find the anchors in it and return them as a list'''
        try:
            parser = HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
            parser.feed(data)
            parser.close()
            return parser.anchorlist
        except:
            print "exception in getAnchors()"
    def findRefs(self,site,data):  #Needs to be relative link aware right now it just finds the base
        '''find links in the page resolve them if they are relative'''
        hrefs = []
        try:
            anchors = self.getAnchors(data)
            anchors = self.relativeToAbsolute(site,anchors)
            tmp = set()
            for x in anchors:
                link = re.findall('(http://[a-zA-Z0-9_\./-]+)',x) #(\.asp.htm|\.html|\.htm*))',x)
                if len(link) > 0:
                    tmp.add(link[0])
            anchors = tmp
            for url in anchors:
                if self.HREFExistsInQue(url) == True:
                    continue
                else:
                    hrefs.append(url)
        except:
            print "Exception in findRefs() :(",site
        #Return a new list or HREFS to be spidered
        return hrefs
    def downloadThread(self,url,name):
        timeStart = time()
        urlretrieve(url,name) #And download it
        timeTaken = time() - timeStart
        self.mediaLog.write(url)
        self.mediaLog.write(strftime(" %a, %d %b %Y %H:%M:%S Downloadtime= " , localtime())+str(timeTaken))
        self.mediaLog.write("\n")
        self.mediaLog.flush()
        self.threadsDownloading -= 1
        print "$$$$ Download complete $$$$: ",url, strftime(" %a, %d %b %Y %H:%M:%S Downloadtime= " , localtime())+str(timeTaken)
    def traverse(self,L = [],loop=1):
        '''Try to implement spider using a Breadth First Search technique instead of Depth First Search'''
        ''' Connect to the page, read all the lines and then look for files and anchors'''
        hrefs = []
        files = []
        data = None
        while(self.stop == False):
                if self.stop == True:
                    print 'about to quit'
                    return 
                sleep(.1)
                self.startcrawlers()
    def HREFExistsInQue(self,href):
        conpool.getConnection()
        b = 0
        try:
            l = True
            hub.begin()
            q = Que.select(Que.q.address == href)
            ql = list(q)            
            if len(ql) > 0:
                hub.end()
                l = False
                return True
            else:
                hub.end()
                l = False
                return False
        except:
            if l == True:
                print 'exception in HREFExistsInQue',b,l
                hub.end()
                return False
            else:
                print 'exception in HREFExistsInQue',b,l
                hub.end()
                return False
    def removeHREFFromQue(self,href):
        conpool.getConnection()
        conpool.getLock()
        hub.begin()
        q = Que.select(Que.q.address == href)
        ql = list(q)
        for x in ql:
            Que.delete(x.id)
        hub.commit()
        hub.end()
        conpool.relLock()
    def addHREFToQue(self,href,t=0.0):
        conpool.getConnection()
        conpool.getLock()
        if len(href) > 0:
            hub.begin()
            sel = User.select(User.q.name == self.user)
            selL = list(sel)
            if len(selL) > 0:
                self.userObj = selL[0]
            else:
                print 'no such user'
            if t != 0.0:
                tn = 0.0
            else:
                tn = time()
            #print href,t,self.userObj
            Que(address=href,time=tn,user=self.userObj)
            hub.commit()
            hub.end()
        conpool.relLock()
    def getHREFSFromQue(self,number):
        #if .next available call it save a bunch of time
        conpool.getConnection()
        #conpool.getLock()
        con = MySQLdb.connect('localhost','root','sniggle','spiderpydb',3306)
        cu = con.cursor()
        sql = "SELECT * FROM que WHERE  user_id = %d ORDER BY time" % self.userid
        rws = cu.execute(sql)
        a= cu.fetchmany(number)
        l = []
        b = set()
        for x in a:
            b.add(x[1])
        for x in b:
            l.append(x)
        cu.close()
        con.close()
        #print l
        #conpool.relLock()
        return l
    def rdata(self,url):
        global threads
        if '\n' in url:
            url = url[:-1]
        t = time()
        print 'connecting to' ,url,'...' 
        f = None
        try:
            import urllib2, httplib
            #httplib.HTTPConnection.debuglevel = 1
            request = urllib2.Request(url)
            request.add_header('Accept-encoding', 'gzip')        
            opener = urllib2.build_opener()
            f = opener.open(request)
            #print f
            if 'gzip' in f.headers.get('Content-Encoding'):
                #print 'gzip found'
                compresseddata = f.read()                              
                #print 'length of the gzip data',len(compresseddata)
                import StringIO
                compressedstream = StringIO.StringIO(compresseddata)   
                import gzip
                gzipper = gzip.GzipFile(fileobj=compressedstream)      
                data = gzipper.read()    
                gzipper.close()
        except:
            #print 'gzip not found'
            #print f
            data = f.read()
            f.close()
        #print 'time taken',time() - t,'data length...',len(data),' bytes'
        return data
    def update_time_q(self,url):
        conpool.getConnection()
        hub.begin()
        selected = URI.select(URI.q.address == url)
        selectedList = list(selected)
        sel = User.select(User.q.name == self.user)
        selList = list(sel)
        delta = 0
        if len(selList) > 0:
            delta = float(selList[0].wait)
        if  len(selectedList) == 0:
            #print 'no uri in db time to get the urls data',url
            hub.end()
            return True
        else:
            for x in selectedList:
                if (time() - float(x.time)) > delta: #here we read the admin table data and compare
                    #print time()- float(x.time)
                    x.time = time()
                    #print 'time to get site data...',url
                    hub.end()
                    return True
                else:
                    #print 'not time to get site data...',url
                    hub.end()
                    return False
    def run(self):
        ''' Start spidering '''
        #connect(1)
        conpool.getConnection()
        hub.begin()
        sites = []
        sel = User.select(User.q.name == self.user)
        selL = list(sel)
        if len(selL) > 0:
            self.userid = selL[0].id+0
            self.userObj = selL[0]
        else:
            print 'no such user'
            hub.end()
            return 
        self.siteSet = {}
        #if q is empty add root sites
        q = Que.select(AND(Que.q.userID == User.q.id,User.q.name == self.user))
        ql = list(q)
        if len(ql) == 0:
            selected = RootSite.select( AND(RootSite.q.userID == User.q.id,User.q.name == self.user) )              
            selectedList = list(selected)
            sites = [ x.address+'' for x in selectedList ]
        hub.end()
        for x in sites:
            self.addHREFToQue(x,1.0)
        self.traverse(sites)
        self.siteLog.close()
        self.mediaLog.close()
        self.exceptionLog.close()
    def startcrawlers(self):
        import math
        tostart = self.MAX_CRAWL_THREADS - self.threads
        if tostart > 0:
            r = self.getHREFSFromQue(tostart)
            if r != False:
                for x in r:
                    if self.update_time_q(x) is True:
                        self.removeHREFFromQue(x)
                        start_new(self.thread,(x,))
                        self.threads += 1
                        #print self.threads
                    #else:
                    #    print 'not time to update',x
            else:
                print 'not enough in que to start threads'
    def thread(self,x):
        data,hrefs,files = None,[],[]
        if x == False:
            print 'no more hrefs to spider'
        try:
            data = self.rdata(x)
        except:
            print 'error connecting to',x                                                               
        try:
            self.processWords(x,data)
        except:
            print 'error with processWords'
        try:
            hrefs = self.findRefs(x,data)
        except:
            print 'error with findRefs in spider',h
            self.exceptionLog.write('error with findRefs in spider() %s' % x)
        try:
            #files = self.findFiles(x,hrefs)
            files = []
            pass
        except:
            print 'error with findFiles in spider()',h
            self.exceptionLog.write('error with findFiles in spider() %s' % x)
        for y in hrefs:
            if y not in files:
                if len(y) > 0:
                    if self.HREFExistsInQue(y) == False and x != y:
                        self.addHREFToQue(y)
            else:
                print 'link found to be a file not html'
        #print "\nFrom %s\nAppended: %s { Files: %s }\n" % (x, hrefs ,files)
        self.threads -= 1
        print self.user,'threads running',self.threads
if __name__ == '__main__':
    s = spider('test')
    s.run()
 
