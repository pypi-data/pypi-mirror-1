from tasty.model import *
import cherrypy
from rest_resource import RESTResource
from dimension import Dimension
from tasty.json import write as jsonify
import turbogears
from turbogears import controllers
from tasty.helpers import sqlobject_to_strings

def build_controllers():
    m = Root()
    s = ServiceController()
    u = UserController()
    i = ItemController()
    t = TagController()

    s.REST_children = {'user' : u, 'item' : i, 'tag'  : t}
    u.REST_children = {'item' : i, 'tag'  : t, 'user' : u}
    i.REST_children = {'user' : u, 'tag'  : t, 'item' : i}
    t.REST_children = {'user' : u, 'item' : i, 'tag' : t}

    s.main = m
    u.main = m
    i.main = m
    t.main = m

    cherrypy.root = m
    cherrypy.root.service = s

class Root(controllers.Root):
    @turbogears.expose()
    def index(self):
        return jsonify([s.name for s in Service.select()])

    obj = {"user" : [], "item" : [], "tag" : [],
           "-user" : [], "-item" : [], "-tag" : []}

    s = None

class ServiceController(RESTResource):
    def REST_instantiate(self,name,**kwargs):
        # reset accumulators. this should probably be done
        # somewhere else. this is kind of dirty.
        self.main.obj["tag"] = []
        self.main.obj["user"] = []
        self.main.obj["item"] = []
        self.main.obj["-user"] = []
        self.main.obj["-item"] = []
        self.main.obj["-tag"] = []
        try:
            s = Service.byName(name.encode('utf8'))
            self.main.s = s
            return s
        except:
            return None
    def REST_create(self,name,**kwargs):
        s = Service(name=name)
        self.main.s = s
        return s

    def index(self,service,**kwargs):
        results = filter_query(service,[],[],[],[],[],[])
        return jsonify(sqlobject_to_strings(results))
    index.expose_resource = True
    def delete(self,service):
        service.destroySelf()
        return "ok"
    delete.expose_resource = True
    def add(self,service):
        # REST_create should have handled everything
        pass
    add.expose_resource = True

    def update(self,service):
        # REST_create should have handled it
        pass
    update.expose_resource = True

    def cloud(self,service):
        results = cloud(service,[],[],[])
        return jsonify(sqlobject_to_strings(results))
    cloud.expose_resource = True



class UserController(Dimension):
    rclass         = User
    r_id_q         = User.q.username
    rclassname     = "user"
    rclass_id_name = "username"

class ItemController(Dimension):
    rclass         = Item
    r_id_q         = Item.q.name
    rclassname     = "item"
    rclass_id_name = "name"

class TagController(Dimension):
    rclass         = Tag
    r_id_q         = Tag.q.name
    rclassname     = "tag"
    rclass_id_name = "name"
