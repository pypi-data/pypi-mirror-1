from sqlobject import *
from turbogears.database import PackageHub
from mx import DateTime

hub = PackageHub("tasty")
__connection__ = hub

class Service(SQLObject):
    name = UnicodeCol(alternateID=True)
    users = MultipleJoin('User')
    items = MultipleJoin('Item')
    tags  = MultipleJoin('Tag')

    def all_rels(self,minus):
        return [(uid.user,uid.item,uid.tag) for uid in UserItemTag.select(
            AND(UserItemTag.q.userID == User.q.id,
                User.q.serviceID == self.id,
                UserItemTag.q.itemID == Item.q.id,
                Item.q.serviceID == self.id,
                UserItemTag.q.tagID == Tag.q.id,
                Tag.q.serviceID == self.id))
                if uid.user not in minus and uid.item not in minus and uid.tag not in minus]

class Orphanable:
    def delete_if_orphan(self):
        if len(self.uits) == 0:
            self.delete()
            
    def possible_orphans(self):
        p = set()
        for t in ['users','items','tags']:
            if hasattr(self,t):
                p.update(set(getattr(self,t)))
        return p

    def del_users(self):
        if hasattr(self,'users'):
            for u in self.users:
                self.removeUser(u)
    def del_items(self):
        if hasattr(self,'items'):
            for i in self.items:
                self.removeItem(i)

    def del_tags(self):
        if hasattr(self,'tags'):
            for t in self.tags:
                self.removeTag(t)

class User(SQLObject,Orphanable):
    class sqlmeta:
        table = "users"
    service = ForeignKey('Service',cascade=True)
    username = UnicodeCol()
    tags = RelatedJoin('Tag')
    items = RelatedJoin('Item')
    uits = MultipleJoin('UserItemTag')    

    fname_s = "username"
    name_s = "user"
    field_s = "user_id"

    def delete(self):
        self.del_items()
        self.del_tags()
        self.destroySelf()

class Tag(SQLObject,Orphanable):
    name = UnicodeCol()
    service = ForeignKey('Service',cascade=True)
    users = RelatedJoin('User')
    items = RelatedJoin('Item')
    uits = MultipleJoin('UserItemTag')
    fname_s = "name"
    name_s = "tag"
    field_s = "tag_id"

    def delete(self):
        self.del_users()
        self.del_items()
        self.destroySelf()


class Item(SQLObject,Orphanable):
    name = UnicodeCol()
    service = ForeignKey('Service',cascade=True)
    users = RelatedJoin('User')
    tags = RelatedJoin('Tag')
    uits = MultipleJoin('UserItemTag')
    
    fname_s = "name"
    name_s = "item"
    field_s = "item_id"

    def delete(self):
        self.del_users()
        self.del_tags()
        self.destroySelf()

class UserItemTag(SQLObject):
    user = ForeignKey('User',cascade=True)
    item = ForeignKey('Item',cascade=True)
    tag  = ForeignKey('Tag',cascade=True)


def add_uit(user,tag,item):
    r = UserItemTag.select(AND(UserItemTag.q.userID    == user.id,
                               UserItemTag.q.tagID     == tag.id,
                               UserItemTag.q.itemID    == item.id))
    if r.count() == 0:
        return UserItemTag(user=user,tag=tag,item=item)
    else:
        return r[0]

def build_all_relationships(users,items,tags):
    for t in tags:
        for u in users:
            if u not in t.users:
                t.addUser(u)
            for i in items:
                if i not in u.items:
                    u.addItem(i)
                add_uit(u,t,i)
        for i in items:
            if i not in t.items:
                t.addItem(i)

def count_zeros(*lists):
    return sum([int(len(l) == 0) for l in lists])


def delete_rels(service,users,items,tags,nusers,nitems,ntags):
    # TODO: minus stuff is ignored
    zeros = count_zeros(users,items,tags)

    # only delete the most specific relationship
    if zeros == 0:
        for u in users:
            for i in items:
                for t in tags:
                    r = UserItemTag.select(AND(UserItemTag.q.userID == u.id,
                                               UserItemTag.q.itemID == i.id,
                                               UserItemTag.q.tagID == t.id))
                if r.count() == 1:
                    r[0].destroySelf()
        return

    if zeros == 1:
        # 2-dimensions
        for user in users:
            for item in items:
                r = UserItemTag.select(AND(UserItemTag.q.userID == user.id,
                                           UserItemTag.q.itemID == item.id))
                for uit in r:
                    uit.destroySelf()
                user.removeItem(item)
            for tag in tags:
                r = UserItemTag.select(AND(UserItemTag.q.userID == user.id,
                                           UserItemTag.q.tagID == tag.id))
                for uit in r:
                    uit.destroySelf()
                user.removeTag(tag)
        for item in items:
            for tag in tags:
                r = UserItemTag.select(AND(UserItemTag.q.itemID == item.id,
                                           UserItemTag.q.tagID == tag.id))
                for uit in r:
                    uit.destroySelf()
                item.removeTag(tag)
        return

    possible_orphans = set()

    for thing in users + items + tags:
        possible_orphans.update(thing.possible_orphans())
        thing.delete()

    for i in possible_orphans:
        i.delete_if_orphan()
    return


def filter_query(service,users,items,tags,nusers,nitems,ntags):
    zeros = count_zeros(users,items,tags)

    if zeros == 0:
        # a query with ALL axis fixed
        # this is either invalid, or i guess
        # we could return a boolean
        return "invalid"

    # minus is our list of things to exclude from the result set
    minus = []
    for u in nusers:
        minus += u.items
        minus += u.tags
    for i in nitems:
        minus += i.users
        minus += i.tags
    for t in ntags:
        minus += t.users
        minus += t.items

    res = {}
    if zeros == 1:
        # two axis fixed
        res = filter_one_variable(users,items,tags,minus)

    if zeros == 2:
        # one axis fixed
        res = filter_two_variables(users,items,tags,minus)

    if zeros == 3:
        # return everything for the whole service
        users = [u for u in User.select(User.q.serviceID == service.id) if u not in minus]
        items = [i for i in Item.select(Item.q.serviceID == service.id) if i not in minus]
        tags =  [t for t in Tag.select(Tag.q.serviceID == service.id) if t not in minus]
        res =  {'users' : users,
                'items' : items,
                'tags' : tags,
                'user_item_tags' : service.all_rels(minus)}
    return res


def construct_where_clause(fixed):
    clauses = [t.field_s + " in (" + ",".join([str(d.id) for d in a]) + ")" for (t,a) in fixed]
    w = ") AND (".join(clauses)
    return w

def fixed_len(fixed):
    fixed_len = 0
    return max([len(a) for (t,a) in fixed])
    for (t,a) in fixed:
        if len(a) > fixed_len:
            fixed_len = len(a)
    return fixed_len

def construct_query(vars,fixed):
    s = ",".join([d.field_s for d in vars])
    where = construct_where_clause(fixed)
    return  "SELECT " + s + " FROM user_item_tag WHERE (" + where + ") GROUP BY " + \
           s + " HAVING count(id) = " + str(fixed_len(fixed))

def filter_one_variable(users,items,tags,minus):
    var = None
    fixed = []

    for (t,a) in [(Tag,tags),(User,users),(Item,items)]:
        if len(a) == 0:
            var = t
        else:
            fixed.append((t,a))

    q = construct_query([var],fixed)

    res = UserItemTag._connection.queryAll(q)
    return {var.name_s + "s" : [v for v in [var.get(i[0]) for i in res] if v not in minus]}

def filter_just_two(var,fixed):
    if len(fixed) == 0: return
    s = set()
    for (typ,l) in fixed:
        for f in l:
            if var == Item:
                for i in f.items:
                    s.add(i)
            if var == User:
                for u in f.users:
                    s.add(u)
            if var == Tag:
                for t in f.tags:
                    s.add(t)
    return list(s)


def filter_two_variables(users,items,tags,minus):
    fixed = None
    vars = []

    for (t,a) in [(Tag,tags),(User,users),(Item,items)]:
        if len(a) != 0:
            fixed = (t,a)
        else:
            vars.append(t)

    q = construct_query(vars,[fixed])
    res = UserItemTag._connection.queryAll(q)

    rdict = {vars[0].name_s + "_" + vars[1].name_s + "s" : [(a,b) for a,b in [(vars[0].get(i[0]),vars[1].get(i[1])) for i in res]
                                                            if a not in minus and b not in minus]}
    for v in vars:
        rdict[v.name_s + "s"] = [x for x in filter_just_two(v,[fixed]) if x not in minus]
    return rdict

def related(service,users,items,tags,nusers,nitems,ntags,limit=10):
    zeros = count_zeros(users,items,tags)

    if zeros == 0:
        # a query with ALL axis fixed
        # this is either invalid, or i guess
        # we could return a boolean
        return "invalid"

    res = filter_query(service,users,items,tags)
    related_items = {}
    related_tags = {}
    related_users = {}
    for t in res.get('tags',[]):
        for i in t.items:
            if i not in items:
                related_items[i] = related_items.get(i,0) + 1
        for u in t.users:
            if u not in users:
                related_users[u] = related_users.get(u,0) + 1
    for u in res.get('users',[]):
        for i in u.items:
            if i not in items:
                related_items[i] = related_items.get(i,0) + 1
        for t in u.tags:
            if t not in tags:
                related_tags[t] = related_tags.get(t,0) + 1
    for i in res.get('items',[]):
        for u in i.users:
            if u not in users:
                related_users[u] = related_users.get(u,0) + 1
        for t in i.tags:
            if t not in tags:
                related_tags[t] = related_tags.get(t,0) + 1
    ritems = [i for i in related_items.keys() if i not in nitems]
    rtags = [t for t in related_tags.keys() if t not in ntags]
    rusers = [u for u in related_users.keys() if u not in nusers]
    ritems.sort(lambda x,y: cmp(related_items[y],related_items[x]))
    rtags.sort(lambda x,y: cmp(related_tags[y],related_tags[x]))
    rusers.sort(lambda x,y: cmp(related_users[y],related_users[x]))
    return {'items' : ritems[:limit],
            'tags' : rtags[:limit],
            'users' : rusers[:limit]}

def cloud(service,users,items,tags):
    zeros = count_zeros(users,items,tags)

    if zeros == 0:
        # can't really produce a cloud for this request
        return "invalid"

    if zeros == 1:
        # two dimensions specified
        var = None
        fixed = []
        for (t,a) in [(User,users),(Item,items),(Tag,tags)]:
            if len(a) == 0:
                var = t
            else:
                fixed.append((t,a))
        q = """select u.%s, count(*) as cnt from user_item_tag uit, %s u
        where uit.%s = u.id AND uit.%s in (%s) and uit.%s in (%s) group by uit.%s,u.%s order by upper(u.%s) ASC""" \
        % (var.fname_s, var.sqlmeta.table, var.field_s, fixed[0][0].field_s,
           ",".join([str(i.id) for i in fixed[0][1]]), fixed[1][0].field_s,
           ",".join([str(i.id) for i in fixed[1][1]]), var.field_s,var.fname_s,var.fname_s)
        return {var.name_s + "s" : [{var.name_s : uit[0], 'count' : uit[1]} for uit in UserItemTag._connection.queryAll(q)]}

    if zeros == 2:
        # one dimension specified
        # TODO: currently returns cloud of the union of multiple items/users/tags
        # should be intersection to be consistent with the rest of the interface
        var = []
        fixed = None
        for (t,a) in [(User,users),(Item,items),(Tag,tags)]:
            if len(a) == 0:
                var.append(t)
            else:
                fixed = (t,a)

        r = {}

        for t in var:
            q = """select u.%s, count(*) as cnt from user_item_tag uit, %s u
            where uit.%s = u.id and uit.%s in (%s) group by uit.%s,u.%s order by upper(u.%s) ASC""" \
            % (t.fname_s,t.sqlmeta.table,t.field_s,fixed[0].field_s,
               ",".join([str(i.id) for i in fixed[1]]),t.field_s,t.fname_s,t.fname_s)
            r[t.name_s + "s"] = [{t.name_s : uit[0], 'count' : uit[1]} for uit in UserItemTag._connection.queryAll(q)]
        return r

    if zeros == 3:
        # /service/<service>/cloud
        # return tag, user, and item clouds
        r = {}
        for t in [User,Item,Tag]:
            q = """select u.%s, count(*) as cnt from user_item_tag uit, %s u
            where uit.%s = u.id and u.service_id = %d group by uit.%s,u.%s order by upper(u.%s) ASC""" \
            % (t.fname_s,t.sqlmeta.table,t.field_s,service.id,t.field_s,t.fname_s,t.fname_s)
            r[t.name_s + "s"] = [{t.name_s : uit[0], 'count' : uit[1]} for uit in UserItemTag._connection.queryAll(q)]

        return r



