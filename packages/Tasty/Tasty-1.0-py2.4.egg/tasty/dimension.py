from rest_resource import RESTResource
from tasty.model import *
from tasty.json import write as jsonify
from tasty.helpers import sqlobject_to_strings

class Dimension(RESTResource):
    """ common base class for user, item, and tag.

    exploits the symmetry of the schema.
    """

    def delete(self,obj):
        delete_rels(self.main.s,self.main.obj["user"],self.main.obj["item"],self.main.obj["tag"],
                     self.main.obj["-user"],self.main.obj["-item"],self.main.obj["-tag"])
        return "ok"

    delete.expose_resource = True

    def index(self,obj,**params):
        results = filter_query(self.main.s,self.main.obj["user"],self.main.obj["item"],self.main.obj["tag"],
                               self.main.obj["-user"],self.main.obj["-item"],self.main.obj["-tag"])
        return jsonify(sqlobject_to_strings(results))
    index.expose_resource = True

    def related(self,obj,limit=10,**params):
        results = related(self.main.s,self.main.obj['user'],self.main.obj['item'],self.main.obj['tag'],
                          self.main.obj["-user"],self.main.obj["-item"],self.main.obj["-tag"],limit=limit)
        return jsonify(sqlobject_to_strings(results))
    related.expose_resource = True

    def add(self,obj,**params):
        if len(self.parents) == 1:
            return "ok"
        build_all_relationships(self.main.obj["user"],self.main.obj["item"],self.main.obj["tag"])
        return "ok"
    add.expose_resource = True

    def update(self,obj,**params):
        if len(self.parents) == 1:
            return "ok"
        build_all_relationships(self.main.obj["user"],self.main.obj["item"],self.main.obj["tag"])
        return "ok"
    update.expose_resource = True


    def list(self,**params):
        results = filter_query(self.main.s,self.main.obj["user"],self.main.obj["item"],self.main.obj["tag"])[self.rclassname + "s"]
        return jsonify(sqlobject_to_strings(results))
    list.expose_resource = True

    def cloud(self,*args,**params):
        results = cloud(self.main.s,self.main.obj["user"],self.main.obj["item"],self.main.obj["tag"])
        return jsonify(sqlobject_to_strings(results))
    cloud.expose_resource = True

    def REST_instantiate(self,id,**kwargs):
        service = self.parents[0]
        try:
            if id[0] == "-":
                # a NOT operator
                id = id[1:]
                o = self.rclass.select(AND(self.r_id_q == id.encode('utf8'),
                                           self.rclass.q.serviceID == service.id))[0]
                self.main.obj["-" + self.rclassname].append(o)
            else:
                o = self.rclass.select(AND(self.r_id_q == id.encode('utf8'),
                                       self.rclass.q.serviceID == service.id))[0]
                self.main.obj[self.rclassname].append(o)
            return o
        except:
            return None

    def REST_create(self,id,**kwargs):
        service = self.parents[0]
        if id[0] == "-":
            o = self.rclass(**dict([(self.rclass_id_name,id[1:]),("service",service)]))
            self.main.obj["-" + self.rclassname].append(o)
        else:
            o = self.rclass(**dict([(self.rclass_id_name,id),("service",service)]))
            self.main.obj[self.rclassname].append(o)
        return o
