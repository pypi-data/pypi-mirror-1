from turbogears.tests import util
from tasty.controllers import build_controllers
from tasty.model import Service,User,Item,Tag,UserItemTag
from tasty.json import read as json_to_obj
import cherrypy,unittest

from turbogears import database
database.set_db_uri("sqlite:///:memory:")
cherrypy.config.update({'global' : {'server.environment' : 'production', 'server.logToScreen' : False}})

def createTables():
    Service.createTable(ifNotExists=True)
    User.createTable(ifNotExists=True)
    Item.createTable(ifNotExists=True)
    Tag.createTable(ifNotExists=True)
    UserItemTag.createTable(ifNotExists=True)

def dropTables():
    UserItemTag.dropTable(ifExists=True)
    Tag.dropTable(ifExists=True)
    Item.dropTable(ifExists=True)
    User.dropTable(ifExists=True)
    Service.dropTable(ifExists=True)

class TastyTest(unittest.TestCase):
    def setUp(self):
        createTables()
        self.service = Service(name="testservice")
        self.user = User(username="testuser",service=self.service)
        self.item = Item(name="testitem",service=self.service)
        self.tag = Tag(name="testtag",service=self.service)


        self.users = dict([(username,User(username=username,service=self.service)) for username in ["anders","jonah","eric","sky","maurice","marc"]])
        self.items = dict([(name,Item(name=name,service=self.service)) for name in ["fernandez fierro","in flames","mastodon","covenant"]])
        self.tags = dict([(name,Tag(name=name,service=self.service)) for name in ["tango","metal","swedish","argentinian","industrial"]])
        build_controllers()


    def tearDown(self):
        dropTables()

def GET(url):
    util.createRequest(url)
    return json_to_obj(cherrypy.response.body[0])

def POST(url):
    util.createRequest(url,method="POST")
    return cherrypy.response

def DELETE(url):
    util.createRequest(url,method="DELETE")
    return cherrypy.response

class TestRoot(TastyTest):
    def test_basics(self):
        "basic test"
        util.createRequest("/")
        body = cherrypy.response.body[0]
        assert ["testservice"] == json_to_obj(body)

class TestService(TastyTest):

    def test_index(self):
        "tests the results of calls to the service"
        r = GET("/service/testservice/")
        assert r.has_key('items')
        assert r.has_key('users')
        assert r.has_key('tags')
        assert r.has_key('user_item_tags')
        assert {u'item' : u'testitem'} in r['items']
        assert {u'user' : u'anders'} in r['users']
        assert {u'tag' : u'swedish'} in r['tags']

    def test_add(self):
        POST("/service/newservice/")
        r = GET("/")
        assert "newservice" in r

    def test_delete(self):
        POST("/service/newservice/")
        r = GET("/")
        assert "newservice" in r
        DELETE("/service/newservice/")
        r = GET("/")
        assert "newservice" not in r

    def test_cloud(self):
        r = GET("/service/testservice/cloud")
        assert r.has_key('tags')
        assert r.has_key('users')
        assert r.has_key('items')

class TestTags(TastyTest):
    def test_basics(self):
        POST("/service/testservice/user/anders/")
        r = GET("/service/testservice/")
        assert r.has_key('users')
        assert {'user' : 'anders'} in r['users']

        r = GET("/service/testservice/user/anders/")
        assert r.has_key('tags')
        assert r.has_key('items')

        assert r['tags'] == []
        assert r['items'] == []

        POST("/service/testservice/user/anders/item/foo/tag/bar/")
        r = GET("/service/testservice/")

        assert {'tag' : 'bar'} in r['tags']
        assert {'item' : 'foo'} in r['items']

        r = GET("/service/testservice/user/anders/")
        assert {'tag' : 'bar'} in r['tags']
        assert {'item' : 'foo'} in r['items']
        assert [{'tag' : 'bar'},{'item' : 'foo'}] in r['tag_items']

        DELETE("/service/testservice/user/anders/")
        r = GET("/service/testservice/")

        assert {'user' : 'anders'} not in r['users']
        assert {'item' : 'foo'} not in r['items']
        assert {'tag' : 'bar'} not in r['tags']
        
    def test_cloud(self):
        r = GET("/service/testservice/cloud")
        assert r['items'] == []
        assert r['users'] == []
        assert r['tags']  == []

        POST("/service/testservice/user/anders/item/foo/tag/bar/")
        POST("/service/testservice/user/anders/item/qux/tag/bar/")

        r = GET("/service/testservice/cloud")
        assert {'item' : 'foo',    'count' : 1} in r['items']
        assert {'tag'  : 'bar',    'count' : 2} in r['tags']
        assert {'user' : 'anders', 'count' : 2} in r['users']

        r = GET("/service/testservice/user/anders/cloud")
        assert {'item' : 'foo','count' : 1} in r['items']
        assert {'tag'  : 'bar','count' : 2} in r['tags']

        r = GET("/service/testservice/item/foo/cloud")
        assert {'tag'  : 'bar',   'count' : 1} in r['tags']
        assert {'user' : 'anders','count' : 1} in r['users']

        r = GET("/service/testservice/tag/bar/cloud")
        assert {'item'  : 'foo',   'count' : 1} in r['items']
        assert {'item'  : 'qux',   'count' : 1} in r['items']
        assert {'user'  : 'anders','count' : 2} in r['users']        
