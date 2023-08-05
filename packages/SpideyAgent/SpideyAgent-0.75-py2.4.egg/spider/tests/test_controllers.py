from turbogears import testutil
from spider.controllers import Root
import cherrypy

cherrypy.root = Root()
q
def test_method():
    #Blank test calls root index
    import types
    result = testutil.call(cherrypy.root.index)

def test_indextitle():
    "The mainpage should have the right title"
    testutil.createRequest("/")
    assert "<TITLE>Welcome to Spiderpy</TITLE>" in cherrypy.response.body[0]

def test_start():
    '''
    Does the spider start ok
    '''
    def create_test_user():
	return 0
	
    def insert_root_site():
	return 0

    create_test_user()
    assert user_in_db()
    insert_root_site()
    assert root_site_in_db()
    s = spider(user)
    assert s.user == 'testuser'
    newthread(s.start())
    
    #how do I check to see if its started?
    #check the que,check the entries decorators?
    
    pass
def test_stop():
    '''
    Does the spider stop ok
    '''
    pass
