# inspired in lovely.tag tag engine

from BTrees import IOBTree, OOBTree
import persistent
from persistent import Persistent
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from zope.app.container.contained import Contained
from zope.interface import implements

from cs.tags.interfaces import ICloudsEngine
import types

#======================================================================
class CloudsEngine(persistent.Persistent, Contained):
    """ """
    implements(ICloudsEngine)

    def __repr__(self):
        try:
            tags = self._all_users_clouds['all_items']['count']
        except:
            tags = 0
        return '<%s tags=%i>' %(self.__class__.__name__, tags)

    def __init__(self):
        """ """
        self._reset()

    def _reset(self):
        """ """
        self._users_clouds = OOBTree.OOBTree()
        self._all_users_clouds = PersistentDict()
        self._all_users_clouds['items'] = IOBTree.IOBTree()
        self._all_users_clouds['all_items'] = PersistentDict()
        self._all_users_clouds['all_items']['cloud'] = OOBTree.OOBTree()
        self._all_users_clouds['all_items']['count'] = 0
        self._all_users_clouds['all_items']['length'] = 0
        self._all_users_clouds['all_items']['aplha'] = PersistentList()
        self._all_users_clouds['all_items']['weight'] = PersistentList()
        self._all_users_clouds['tags'] = OOBTree.OOBTree()


    def delete(self, item=None, user=None, tags=None):
        """ """
        this_user_clouds = self._users_clouds.get(user,None)
        if this_user_clouds != None:
           this_user_this_item_clouds =  this_user_clouds['items'].get(item,None)
           if this_user_this_item_clouds != None:
              # delete
              for tagname in tags:
                  this_user_this_item_this_tag = this_user_this_item_clouds['cloud'].get(tagname,None)
                  if this_user_this_item_this_tag != None:
                      if this_user_this_item_clouds['cloud'][tagname] == 1:
                          del this_user_this_item_clouds['cloud'][tagname]
                          this_user_this_item_clouds['length'] -= 1
                      else:
                          this_user_this_item_clouds['cloud'][tagname] -= 1
                      this_user_this_item_clouds['count'] -= 1
              
                                                       
              l = [(i[0],i[1]) for i in this_user_this_item_clouds['cloud'].items()]
              l.sort(lambda x,y:cmp(x[0],y[0]))
              this_user_this_item_clouds['alpha'] = PersistentList(l)
              l = [(i[0],i[1]) for i in this_user_this_item_clouds['cloud'].items()]
              l.sort(lambda x,y:y[1]-x[1])
              this_user_this_item_clouds['weight'] = PersistentList(l)


           this_user_all_items_clouds = this_user_clouds['all_items']
           # delete
           for tagname in tags:
               this_user_all_items_this_tag = this_user_all_items_clouds['cloud'].get(tagname,None)
               if this_user_all_items_this_tag != None:
                   if this_user_all_items_clouds['cloud'][tagname] == 1:
                       del this_user_all_items_clouds['cloud'][tagname]
                       this_user_all_items_clouds['length'] -= 1
                   else:
                       this_user_all_items_clouds['cloud'][tagname] -= 1
                   this_user_all_items_clouds['count'] -= 1

           l = [(i[0],i[1]) for i in this_user_all_items_clouds['cloud'].items()]
           l.sort(lambda x,y:cmp(x[0],y[0]))
           this_user_all_items_clouds['alpha'] = PersistentList(l)
           l = [(i[0],i[1]) for i in this_user_all_items_clouds['cloud'].items()]
           l.sort(lambda x,y:y[1]-x[1])
           this_user_all_items_clouds['weight'] = PersistentList(l)


        all_users_clouds = self._all_users_clouds

        all_users_this_item_clouds =  all_users_clouds['items'].get(item,None)
        if all_users_this_item_clouds != None:
            # delete
            for tagname in tags:
                all_users_this_item_this_tag = all_users_this_item_clouds['cloud'].get(tagname,None)
                if all_users_this_item_this_tag != None:
                    if all_users_this_item_clouds['cloud'][tagname] == 1:
                        del all_users_this_item_clouds['cloud'][tagname]
                        all_users_this_item_clouds['length'] -= 1
                    else:
                        all_users_this_item_clouds['cloud'][tagname] -= 1
                    all_users_this_item_clouds['count'] -= 1
              
                                                       
            l = [(i[0],i[1]) for i in all_users_this_item_clouds['cloud'].items()]
            l.sort(lambda x,y:cmp(x[0],y[0]))
            all_users_this_item_clouds['alpha'] = PersistentList(l)
            l = [(i[0],i[1]) for i in all_users_this_item_clouds['cloud'].items()]
            l.sort(lambda x,y:y[1]-x[1])
            all_users_this_item_clouds['weight'] = PersistentList(l)

        all_users_all_items_clouds = all_users_clouds['all_items']
        # delete
        for tagname in tags:
            all_users_all_items_this_tag = all_users_all_items_clouds['cloud'].get(tagname,None)
            if all_users_all_items_this_tag != None:
                if all_users_all_items_clouds['cloud'][tagname] == 1:
                    del all_users_all_items_clouds['cloud'][tagname]
                    all_users_all_items_clouds['length'] -= 1
                else:
                    all_users_all_items_clouds['cloud'][tagname] -= 1
                all_users_all_items_clouds['count'] -= 1
              
                                                       
        l = [(i[0],i[1]) for i in all_users_all_items_clouds['cloud'].items()]
        l.sort(lambda x,y:cmp(x[0],y[0]))
        all_users_all_items_clouds['alpha'] = PersistentList(l)
        l = [(i[0],i[1]) for i in all_users_all_items_clouds['cloud'].items()]
        l.sort(lambda x,y:y[1]-x[1])
        all_users_all_items_clouds['weight'] = PersistentList(l)


    def update(self, item, user, tags):
        """ """
        add_tags = tags

	try:
           this_user_clouds = self._users_clouds.get(user,None)
        except:
           self._users_clouds = OOBTree.OOBTree()
           this_user_clouds = self._users_clouds.get(user,None)

        if this_user_clouds == None: 
           this_user_clouds = PersistentDict()
           this_user_clouds['items'] = IOBTree.IOBTree()
           this_user_clouds['all_items'] = PersistentDict()
           this_user_clouds['all_items']['cloud'] = OOBTree.OOBTree()
           this_user_clouds['all_items']['count'] = 0
           this_user_clouds['all_items']['length'] = 0
           this_user_clouds['all_items']['aplha'] = PersistentList()
           this_user_clouds['all_items']['weight'] = PersistentList()

	   self._users_clouds[user] = this_user_clouds

        this_user_this_item_clouds = this_user_clouds['items'].get(item,None)
        if this_user_this_item_clouds == None:
           this_user_this_item_clouds = PersistentDict()
           this_user_this_item_clouds['cloud'] = OOBTree.OOBTree()
           this_user_this_item_clouds['count'] = 0
           this_user_this_item_clouds['length'] = 0
           this_user_this_item_clouds['aplha'] = PersistentList()
           this_user_this_item_clouds['weight'] = PersistentList()
           this_user_clouds['items'][item] = this_user_this_item_clouds

        this_user_all_items_clouds = this_user_clouds['all_items']

        for tagname in add_tags:
           # this item
           this_user_this_item_this_tag = this_user_this_item_clouds['cloud'].get(tagname,None)
           if this_user_this_item_this_tag == None :
              this_user_this_item_this_tag = 1
              this_user_this_item_clouds['length'] += 1
           else:
              this_user_this_item_this_tag += 1
           this_user_this_item_clouds['cloud'][tagname] = this_user_this_item_this_tag
           this_user_this_item_clouds['count'] += 1
           
           # all items
           this_user_all_items_this_tag = this_user_clouds['all_items']['cloud'].get(tagname,None)
           if this_user_all_items_this_tag == None :
              this_user_all_items_this_tag = 1
              this_user_all_items_clouds['length'] += 1
           else:
              this_user_all_items_this_tag += 1
           this_user_all_items_clouds['cloud'][tagname] = this_user_all_items_this_tag
           this_user_all_items_clouds['count'] += 1

        l = [(i[0],i[1]) for i in this_user_this_item_clouds['cloud'].items()]
        l.sort(lambda x,y:cmp(x[0],y[0]))
        this_user_this_item_clouds['alpha'] = PersistentList(l)
        l = [(i[0],i[1]) for i in this_user_this_item_clouds['cloud'].items()]
        l.sort(lambda x,y:y[1]-x[1])
        this_user_this_item_clouds['weight'] = PersistentList(l)
        l = [(i[0],i[1]) for i in this_user_all_items_clouds['cloud'].items()]
        l.sort(lambda x,y:cmp(x[0],y[0]))
        this_user_all_items_clouds['alpha'] = PersistentList(l)
        l = [(i[0],i[1]) for i in this_user_all_items_clouds['cloud'].items()]
        l.sort(lambda x,y:y[1]-x[1])
        this_user_all_items_clouds['weight'] = PersistentList(l)

        # manage all users clouds

        try:
           all_users_clouds = self._all_users_clouds
        except:
           self._all_users_clouds = PersistentDict()
           self._all_users_clouds['items'] = IOBTree.IOBTree()
           self._all_users_clouds['all_items'] = PersistentDict()
           self._all_users_clouds['all_items']['cloud'] = OOBTree.OOBTree()
           self._all_users_clouds['all_items']['count'] = 0
           self._all_users_clouds['all_items']['length'] = 0
           self._all_users_clouds['aplha'] = PersistentList()
           self._all_users_clouds['weight'] = PersistentList()
           self._all_users_clouds['tags'] = OOBTree.OOBTree()
           all_users_clouds = self._all_users_clouds

        all_users_this_item_clouds =  all_users_clouds['items'].get(item,None)
        if all_users_this_item_clouds == None:
           all_users_this_item_clouds = PersistentDict()
           all_users_this_item_clouds['cloud'] = OOBTree.OOBTree()
           all_users_this_item_clouds['count'] = 0
           all_users_this_item_clouds['length'] = 0
           all_users_this_item_clouds['aplha'] = PersistentList()
           all_users_this_item_clouds['weight'] = PersistentList()
           all_users_clouds['items'][item] = all_users_this_item_clouds

        all_users_all_items_clouds = all_users_clouds['all_items']

        for tagname in add_tags:
           # this item
           all_users_this_item_this_tag = all_users_this_item_clouds['cloud'].get(tagname,None)
           if all_users_this_item_this_tag == None :
              all_users_this_item_this_tag = 1
              all_users_this_item_clouds['length'] += 1
           else:
              all_users_this_item_this_tag += 1
           all_users_this_item_clouds['cloud'][tagname] = all_users_this_item_this_tag
           all_users_this_item_clouds['count'] += 1
           
           # all items
           all_users_all_items_this_tag = all_users_clouds['all_items']['cloud'].get(tagname,None)
           if all_users_all_items_this_tag == None :
              all_users_all_items_this_tag = 1
              all_users_all_items_clouds['length'] += 1
           else:
              all_users_all_items_this_tag += 1
           all_users_all_items_clouds['cloud'][tagname] = all_users_all_items_this_tag
           all_users_all_items_clouds['count'] += 1

           self._all_users_clouds['tags']
           all_users_this_tag =  self._all_users_clouds['tags'].get(tagname,None)
           if all_users_this_tag == None:
              all_users_this_tag = PersistentDict()
              all_users_this_tag['items'] = PersistentList()
           all_users_this_tag['items'].append(item)
           self._all_users_clouds['tags'][tagname] = all_users_this_tag

        l = [(i[0],i[1]) for i in all_users_this_item_clouds['cloud'].items()]
        l.sort(lambda x,y:cmp(x[0],y[0]))
        all_users_this_item_clouds['alpha'] = PersistentList(l)
        l = [(i[0],i[1]) for i in all_users_this_item_clouds['cloud'].items()]
        l.sort(lambda x,y:y[1]-x[1])
        all_users_this_item_clouds['weight'] = PersistentList(l)
        l = [(i[0],i[1]) for i in all_users_all_items_clouds['cloud'].items()]
        l.sort(lambda x,y:cmp(x[0],y[0]))
        all_users_all_items_clouds['alpha'] = PersistentList(l)
        l = [(i[0],i[1]) for i in all_users_all_items_clouds['cloud'].items()]
        l.sort(lambda x,y:y[1]-x[1])
        all_users_all_items_clouds['weight'] = PersistentList(l)


    def getRelatedTags(self, tag, n=40):
        """ """
        try:
          items = set(self._all_users_clouds['tags'][tag]['items'])
          tags = self._all_users_clouds['tags'].keys()
          d=[]
          c=0
          l=0
          for other_tag in tags:
            if other_tag != tag:
               other_tags_items = set(self._all_users_clouds['tags'][other_tag]['items'])
               items_in_common = len(items.intersection(other_tags_items))
               if items_in_common > 1:
                  d.append((other_tag,items_in_common))
                  c+=items_in_common
                  l+=1
	  d.sort(lambda x,y:x[1]-y[1])
          d=d[:n]
        except:
          d = []
          c = 0
          l = 0
        if l>n:l=n
        return (d,c,l)

    def getRelatedItems(self, item, n=40):
        """ """
        try:
          tags = set(self._all_users_clouds['items'][item]['cloud'].keys())
          items = self._all_users_clouds['items'].keys()
          d=[]
          c=0
          l=0
          for other_item in items:
            if other_item != item:
               other_items_tags = set(self._all_users_clouds['items'][other_item]['cloud'].keys())
               tags_in_common = len(tags.intersection(other_items_tags))
               if tags_in_common > 0:
                  d.append((other_item,tags_in_common))
                  c+=tags_in_common
                  l+=1
	  d.sort(lambda x,y:x[1]-y[1])
          d=d[:n]
        except:
          d = []
          c = 0
          l = 0
        if l>n:l=n
        return (d,c,l)

    def getRelatedUsers(self, user, n=40):
        """ """
        try:
          tags = set(self._users_clouds[user]['all_items']['cloud'].keys())
          users = self._users_clouds.keys()
          d=[]
          c=0
          l=0
          for other_user in users:
            if other_user != user:
               other_users_tags = set(self._users_clouds[other_user]['all_items']['cloud'].keys())
               tags_in_common = len(tags.intersection(other_users_tags))
               if tags_in_common > 0:
                  d.append((other_user,tags_in_common))
                  c+=tags_in_common
                  l+=1
	  d.sort(lambda x,y:x[1]-y[1])
          d=d[:n]
        except:
          d=[]
          c=0
          l=0
        if l>n:l=n
        return (d,c,l)


    def getCloud(self, items=None, users=None, n=40):
        """ """
        
        if type(items) == types.IntType:
            items = [items]
        if type(users) in types.StringTypes:
            users = [users]

        if items == None: items = []
        if users == None: users = []

        if len(items)==0 and len(users)==0:
           try:
               d = self._all_users_clouds['all_items']['weight'][:n]
               c = self._all_users_clouds['all_items']['count']
               l = self._all_users_clouds['all_items']['length']
           except:
               d = []
               c = 0
               l = 0
           if l>n:l=n
           return (d,c,l)

        if len(items)==1 and len(users)==1:
           user = users[0]
           item = items[0]
           try:
               d = self._users_clouds[user]['items'][item]['weight'][:n]
               c = self._users_clouds[user]['items'][item]['count']
               l = self._users_clouds[user]['items'][item]['length']
           except:
               d = []
               c = 0
               l = 0
           if l>n:l=n
           return (d,c,l)

        if len(users)==1:
           user = users[0]
           try:
               d = self._users_clouds[user]['all_items']['weight'][:n]
               c = self._users_clouds[user]['all_items']['count']
               l = self._users_clouds[user]['all_items']['length']
               if l>n:l=n
           except:
               d = []
               c = 0
               l = 0
           return (d,c,l)

        if len(items)==1:
           item = items[0]
           try:
               d = self._all_users_clouds['items'][item]['weight'][:n]
               c = self._all_users_clouds['items'][item]['count']
               l = self._all_users_clouds['items'][item]['length']
           except:
               d = []
               c = 0
               l = 0
           if l>n:l=n
           return (d,c,l)

        return ([],0,0)
