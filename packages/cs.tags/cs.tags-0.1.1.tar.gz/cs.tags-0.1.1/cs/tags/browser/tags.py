from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher.browser import BrowserPage

from kelpi.tags.interfaces import ICloudsEngine
from kelpi.syndication.syndication import RESERVED_NAMES as RSS_NAMES

class TagsReader(BrowserPage):

    template = ViewPageTemplateFile('tags.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def tags(self, user=None):

        clouds_engine = zapi.getUtility(ICloudsEngine)

        if user != None:
            usersl = []
            usersl.append(user)
            cloud,c,l = clouds_engine.getCloud(users=usersl)
        else:
            cloud,c,l = clouds_engine.getCloud()

        #--------- let's modify cloud: calculate font size based on the metric value of the tag ---------
        font_size_dict = {}
        distinct_metric_values = [t for t in set([c[1] for c in cloud])]
        distinct_metric_values.sort(lambda x,y:y-x)
        ldmv = len(distinct_metric_values)
        bunch = ldmv/5

        if bunch==0:
           bunch=1
            
        for font_size in range(1,6):
            beg=(font_size-1)*bunch
            end=(font_size)*bunch
            if font_size==5:end=ldmv
            for n in range(beg,end):
                try:  
                 font_size_dict[distinct_metric_values[n]] = 's'+str(font_size)
                except:
                 pass

        for n in range(len(cloud)):
            cloud[n]=(cloud[n][0],font_size_dict[cloud[n][1]])
        #----------------------------------------------------------------------------------------------- 

        cloud.sort(lambda x,y:cmp(x[0].lower(),y[0].lower()))
        return cloud,c,l

    def related_tags(self, tag=None):

        clouds_engine = zapi.getUtility(ICloudsEngine)

        if tag != None:
            cloud,c,l = clouds_engine.getRelatedTags(tag)
        else:
            cloud,c,l = ([],0,0)

        #--------- let's modify cloud: calculate font size based on the metric value of the tag ---------
        font_size_dict = {}
        distinct_metric_values = [t for t in set([c[1] for c in cloud])]
        distinct_metric_values.sort(lambda x,y:y-x)
        ldmv = len(distinct_metric_values)
        bunch = ldmv/5

        if bunch==0:
           bunch=1
            
        for font_size in range(1,6):
            beg=(font_size-1)*bunch
            end=(font_size)*bunch
            if font_size==5:end=ldmv
            for n in range(beg,end):
                try:  
                 font_size_dict[distinct_metric_values[n]] = 's'+str(font_size)
                except:
                 pass

        for n in range(len(cloud)):
            cloud[n]=(cloud[n][0],font_size_dict[cloud[n][1]])
        #----------------------------------------------------------------------------------------------- 

        cloud.sort(lambda x,y:cmp(x[0].lower(),y[0].lower()))
        return cloud,c,l

    def related_users(self, user=None):

        clouds_engine = zapi.getUtility(ICloudsEngine)

        if user != None:
            cloud,c,l = clouds_engine.getRelatedUsers(user)
        else:
            cloud,c,l = ([],0,0)

        #--------- let's modify cloud: calculate font size based on the metric value of the tag ---------
        font_size_dict = {}
        distinct_metric_values = [t for t in set([c[1] for c in cloud])]
        distinct_metric_values.sort(lambda x,y:y-x)
        ldmv = len(distinct_metric_values)
        bunch = ldmv/5

        if bunch==0:
           bunch=1
            
        for font_size in range(1,6):
            beg=(font_size-1)*bunch
            end=(font_size)*bunch
            if font_size==5:end=ldmv
            for n in range(beg,end):
                try:  
                 font_size_dict[distinct_metric_values[n]] = 's'+str(font_size)
                except:
                 pass

        for n in range(len(cloud)):
            cloud[n]=(cloud[n][0],font_size_dict[cloud[n][1]])
        #----------------------------------------------------------------------------------------------- 

        cloud.sort(lambda x,y:cmp(x[0].lower(),y[0].lower()))
        return cloud,c,l



    def __call__(self):
        """ """
        if len(self.traverse_subpath)>0:
           if self.traverse_subpath[-1] in RSS_NAMES :
              return getMultiAdapter((self, self.request), name=self.traverse_subpath[-1])()
        return self.template()
