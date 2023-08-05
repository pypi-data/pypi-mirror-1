import turbogears
from model import *
from docutils.core import publish_parts
import cherrypy
import re
from sqlobject import SQLObjectNotFound
from turbogears import validators
import spider
from thread import *
import os
from cPickle import *
from time import *
from string import *
s = None
spiders = []
'''
BUGS: Start Stop not working well
TODO: Add home button to user validate page, also show the users name and provide a way to change their password
TODO: Add AJAX view of whats going on in the interpreter as far as what site is being visited
TODO: Add threading for fun
There need to be several things done so that this tool can be more useable
    * the interface needs to be improved and made as consistent as possible
    * the useage of the system needs to be changes so that each user can have multiple spiders running to allow searches on specific sites
        this would mean rewriting the templates and the model structure, right now its ok but it could implement this and be better
    * the spiders themselves need to be database safe
        * they also need to be threaded perhaps to use more than one processor (try just threading find every word first)
            * this would be a good candidate for a branch
    * speed issues need to be addressed
    * AJAX could help the user view their results
'''

class Root:
    def __init__(self):
        self.master_dict = {}
        connect(1)
    @turbogears.expose(html="spider.templates.welcome")
    def index(self):
        return dict(data="")
    @turbogears.expose(html="spider.templates.results")
    def search(self,data=None,username='',page=1,submit=None):
        #Use the user entered search string for searching in the database
        #calculate the number of pages
        print username
        page = int(page)
        conpool.getConnection()
        words = data.split()
        resultsperpage = 20
        number = len(words)
        sites  = []
        Union = set()
        a = set()
        descriptions = {}
        #check to see if all words make a union of their href sets
        for x in words:
            #print x
            selected = Entry.select(Entry.q.word == x)
            selected_as_list = list(selected)
            a = set()
            #select the word in the database if it exists
            if  len(selected_as_list) > 0:
                #if there is currently an empty union of sites
                if len(Union) == 0:
                    for y in selected_as_list:
                            if y.user.name == username or username == '':
                                Union.add(str(y.uri.address))
                            else:
                                pass
                #if there are already some sites associated with one or more of the words we are searching for
                else:
                    for y in selected_as_list:
                        #for x in y.entries:
                            if y.user.name == username or username == '':
                                #add the word to a set to check against the union
                                a.add(y.uri.address+'')
                    #if the word appears in sites in the union as well then those common sites will remain in the list of matching sites that the user will then select from
                    Union = a.intersection(Union)
            else:
                Union = set()
                break
        sites = list(Union)
        numberofpages = 1+len(sites) / resultsperpage
        sites = sites[(page)*resultsperpage:(1+page)*resultsperpage] # we could refine this set to include only the best sites using some alg like size * links or size or page rank or the option to choose
        #the template needs a list of hrefs and descriptions, and a marker(page number) for the position of the results and then if next the new position is calculated if previous then it is calculated if a page number is selected then it is passed.
        #the amount of results on the page should be a user editable variable
        #this goes in the template <a href=${tg.url('/',nextsearchpage,)}
        #print sites
        #get a sample of the text where the word/words appear 1 or 2 lines
        for each in sites:
            u = URI.select(URI.q.address == each)
            l = list(u)
            for site in l:
                for word in words:
                    lines = 0
                    #if there is already a preview of the site then do nothing
                    if descriptions.has_key(site.address):
                       pass
                    else:
                        #get words from the data
                        def getworddata(data):
                            showing = re.sub('<[^>]*>', '', data)
                            words = re.findall('\w+',showing)
                            return words
                        wds = getworddata(site.data)
                        wds_ = ' '.join(wds)
                        ln = len(wds_)
                        #find where the word is in the data
                        start = find(wds_,word)
                        #!here we need to add a line for each word hit or the union of multiple words on a line
                        #copy the site data into the dictionary descriptions to be shown to the user
                        #some unwanted text sometimes appears such as t t t or bsp what to do? Some sites don't seem to find matches investigate!
                        if ln >= start+100:
                            descriptions[site.address] = wds_[start:start+100]
                        else:
                            descriptions[site.address] = wds_[start:-1]
        return dict(username=username,data=data,descriptions=descriptions,words=words,sites=sites,numberofpages=numberofpages,page=page)
    @turbogears.expose(html="spider.templates.authenticateAdmin")
    def admin(self):
        return dict()
    @turbogears.expose(html="spider.templates.admin")
    def adminAuth(self,password,submit=''):
        conpool.getConnection()
        selected = Admin.select()
        selL = list(selected)
        if len(selL) > 0:
            a = selL[0]
            if a.password == password:
                selected = User.select()
                selected_as_list = list(selected)
                users = [x.name for x in selected_as_list]
                return dict(users=users)
            else:
                return 'Password does not match'
        else:
            b = Admin(password='admin',email='admin@business.com')
            return 'No administrator has logged in yet so the default admin user has been created with a login password "admin"'
        
    @turbogears.expose(html="spider.templates.login")
    def login(self):
        #show the custom searches the user has made [search strings,media types,sites to search]
        return dict()
    @turbogears.expose(html="spider.templates.newuser")
    def newuser(self):
        return dict()
    @turbogears.expose(html="spider.templates.userpage")
    def validateuser(self,username,password='',submit=''):
        print username
        conpool.getConnection()
        def wrds(u):
            sel = User.select(User.q.name == u)
            selL = list(sel)
            if len(selL) > 0:
                #print 'User exists validated'
                print Entry.q
                l = Entry.select(Entry.q.userID == selL[0].id)
                l = list(l)
                #print len(l)
                return len(l)
            return 0
        def sites(u):
            ss = set()
            sel = User.select(User.q.name == u)
            selL = list(sel)
            if len(selL) > 0:
                #print 'User exists validated'
                print Entry.q
                l = Entry.select(Entry.q.userID == selL[0].id)
                ll = list(l)
                for x in ll:
                    ss.add(x.uriID)
                #print len(ss)
                return len(ss)
            return 0
        def nq(u):
            sel = User.select(User.q.name == u)
            selL = list(sel)
            if len(selL) > 0:
                q = Que.select(Que.q.userID == selL[0].id)
                ql = list(q)
                #print len(ql)
                return len(ql)
            return 0
                
        root_sites = []
        time = ''
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            print 'User exists validated'
            time = selL[0].wait
        else:
            return 'User does not exist'
        root_sites = [x.address for x in selL[0].rootSites]
        numberofwords= 0# wrds(username)
        numberofsites= 0#sites(username)
        numberinque = 0#nq(username)
        #word_cnt = wordsFound(username)
        #site_cnt = sitesSpidered(username)
        #sites_in_que = sitesInQue(username)
        return dict(username=username,password=password,time = time,root_sites=root_sites,numberofwords=numberofwords,numberofsites=numberofsites,numberinque=numberinque)
    @turbogears.expose(html="spider.templates.login")
    def createuser(self,username,password,email,interval,submit):
        conpool.getConnection()
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            return 'User already exists'
        else:
            interval = str(interval)
            wait = interval
            u = User(name=username,password=password,email=email,wait=wait)
        root_sites = [ x.adress for x in u.rootSites] 
        #return dict(username=username,password=password,time = interval,root_sites=root_sites)
        return dict()
    @turbogears.expose(html="spider.templates.userpage")
    def start(self,username,submit):
        conpool.getConnection()
        global s,spiders
        #Check to see if its already running
        for x in spiders:
            if x.user == username:
                return 'already running'
                    
        hub.begin()
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            print selL[0].name
        else:
            hub.end()
            return 'No such user'
        hub.end()
        try:
            s = spider.spider(username)
            spiders.append(s)
            start_new(s.run,())
            print 'thread started'
        except:
            print 'error while trying to start spider thread'
            pass
        def wrds(u):
            sel = User.select(User.q.name == u)
            selL = list(sel)
            if len(selL) > 0:
                #print 'User exists validated'
                print Entry.q
                l = Entry.select(Entry.q.userID == selL[0].id)
                l = list(l)
                #print len(l)
                return len(l)
            return 0
        def sites(u):
            ss = set()
            sel = User.select(User.q.name == u)
            selL = list(sel)
            if len(selL) > 0:
                #print 'User exists validated'
                print Entry.q
                l = Entry.select(Entry.q.userID == selL[0].id)
                ll = list(l)
                for x in ll:
                    ss.add(x.uriID)
                #print len(ss)
                return len(ss)
            return 0
        def nq(u):
            sel = User.select(User.q.name == u)
            selL = list(sel)
            if len(selL) > 0:
                q = Que.select(Que.q.userID == selL[0].id)
                ql = list(q)
                #print len(ql)
                return len(ql)
            return 0
                
        root_sites = []
        time = ''
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            print 'User exists validated'
            time = selL[0].wait
        else:
            return 'User does not exist'
        root_sites = [x.address for x in selL[0].rootSites]
        numberofwords= 0# wrds(username)
        numberofsites= 0#sites(username)
        numberinque = 0#nq(username)
        #word_cnt = wordsFound(username)
        #site_cnt = sitesSpidered(username)
        #sites_in_que = sitesInQue(username)
        return dict(username=username,password='',time = time,root_sites=root_sites,numberofwords=numberofwords,numberofsites=numberofsites,numberinque=numberinque)
        
    @turbogears.expose(html="spider.templates.stop")
    def stop(self,username,submit):
        for x in spiders:
            if x.user == username:
                x.stop = True
                sleep(.1) #dangerous
                spiders.remove(x) #dangerous
        return dict()
    @turbogears.expose(html="spider.templates.add")
    def add(self,username,submit):
        return dict(username=username)
    @turbogears.expose(html="spider.templates.remove")
    def remove(self,username,submit):
        return dict()
    @turbogears.expose(html="spider.templates.userpage")
    def insertNewSite(self,address,username,submit):
        print 'inserting new site'
        conpool.getConnection()
        hub.begin()
        #here we need to insert data into the table
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            user = selL[0]
            password = user.password +''
            ns = RootSite(address=address,user=user)
        else:
            hub.end()
            return 'no such user %s, cannot insert ' % username
        #if spidering just spider the root site not out of the main site
        hub.commit()
        root_sites = []
        time = ''
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            print 'User exists validated'
            time = selL[0].wait
        else:
            return 'User does not exist'
        root_sites = [x.address for x in selL[0].rootSites]
        numberofwords= 0# wrds(username)
        numberofsites= 0#sites(username)
        numberinque = 0#nq(username)
        hub.end()
        return dict(username=username,password=password,time = time,root_sites=root_sites,numberofwords=numberofwords,numberofsites=numberofsites,numberinque=numberinque)
    @turbogears.expose(html="spider.templates.userpage")
    def deleteSite(self,user,address,submit):
        username = user
        conpool.getConnection()
        hub.begin()
        sel = User.select(User.q.name == user)
        selL = list(sel)
        sites = selL[0].rootSites
        for x in sites:
            if x.address == address:
                RootSite.delete(x.id)
        hub.commit()
        root_sites = []
        time = ''
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            print 'User exists validated'
            time = selL[0].wait
            usr = selL[0]
            password = usr.password+''
        else:
            return 'User does not exist'
        root_sites = [x.address for x in selL[0].rootSites]
        numberofwords= 0# wrds(username)
        numberofsites= 0#sites(username)
        numberinque = 0#nq(username)
        hub.end()
        return dict(username=username,password=password,time = time,root_sites=root_sites,numberofwords=numberofwords,numberofsites=numberofsites,numberinque=numberinque)
    @turbogears.expose(html="spider.templates.setInterval")
    def setInterval(self,username,submit,time):
        conpool.getConnection()
        hub.begin()
        sel = User.select(User.q.name == username)
        selectedList = list(sel)
        time = int(time)
        if len(selectedList) == 1:
            selectedList[0].wait = time
        hub.commit()
        hub.end()
        return "Update interval has been set to %d" % time
    @turbogears.expose()
    def clearQ(self,username,submit):
        conpool.getConnection()
        hub.begin()
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            usr = selL[0]
            #print usr.que,'<-- list to be deleted'
            for x in usr.que:
                Que.delete(x.id)
        ps = usr.que + ['']
        print usr.que
        hub.commit()
        hub.end()
        return  str(ps)
    @turbogears.expose()
    def setMedia(self,mpg='off',avi='off',wmv='off',submit=None):
        return mpg+avi+wmv
    @turbogears.expose(html="spider.templates.edit_user")
    def edit_user(self,username,submit=None):
        conpool.getConnection()
        hub.begin()
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            usr = selL[0]
        else:
            hub.end()
            return 'error with getting the users data'
        name=usr.name+''
        password=usr.password+''
        email=usr.email+''
        interval=str(usr.wait)+''
        rootSites=usr.rootSites+[]
        que=usr.que+[]
        hub.end()
        return dict(name=name,password=password,email=email,interval=interval,rootSites=rootSites,que=que)
    @turbogears.expose(html="spider.templates.admin")
    def save_changes(self,username,password,email,interval,submit=None):
        conpool.getConnection()
        hub.begin()
        sel = User.select(User.q.name == username)
        selL = list(sel)
        if len(selL) > 0:
            usr = selL[0]
        else:
            hub.end()
            return 'error with getting the users data'
        usr.name = username
        usr.password = password
        usr.email = email
        hub.commit()
        hub.end()
        return self.admin()
