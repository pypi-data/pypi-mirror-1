from Globals import INSTANCE_HOME, InitializeClass
import os, shutil
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import getToolByName
from random import choice, randint, shuffle
from urllib import urlopen
from xml.dom.minidom import parseString
import re
from StringIO import StringIO

class ContentSetup:
    """ Customises Plone for load testing by creating content """

    bbc = 'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/%s/rss.xml'
    feeds = [
        'front_page','world','uk','business','uk_politics','health','education',
        'sci/tech','technology','entertainment','talking_point','magazine'
        ]

    flickr = 'http://api.flickr.com/services/feeds/photos_public.gne'
    flickr += '?tags=%s&format=rss2'
    ftags = ['plone','tree','zope','people','python','flower','ilrt','netsight']

    def __init__(self):
        self.BASE_PRODUCTS = []
        self.out = []
        self.somedata = {}
        
    def customize(self, portal, context, settings={}, logging='log'):
        """ Run the portal customisation methods that generate content """
        self.out = []
        profile = settings.get('profile','intranet')
        sectioncount = settings.get('sectioncount',3)
        foldercount=settings.get('foldercount',5)
        if self.checkZEXP(profile,sectioncount):
            self.addZEXPContent(portal, 
                                sectioncount=sectioncount, profile=profile)
        else:
            self.leechSomeData(settings=settings)
            self.addContent(portal,sectioncount=sectioncount,
                       foldercount=foldercount, 
                       itemcount=settings.get('itemcount',10),
                       imagecount=settings.get('imagecount',5),
                       bigimagecount=settings.get('bigimagecount',5),                            
                       profile=profile)
            self.exportZEXPContent(portal,
                                   sectioncount=sectioncount,
                                   profile=profile)

        self.cloneContent(portal,
                          multiply=settings.get('multiply',2),
                          sectioncount=sectioncount,
                          foldercount=foldercount, 
                          profile=profile)
        
        if logging == 'debug':
            error = ''
            for line in self.out:
                if line:
                    error += str(line)
            if error:
                raise error
        else:
            # TODO: Add writing of this to the generic setup log
            return
        
    def leechSomeData(self, settings):
        """ Leech some data from the BBC's and Flickr's rss feeds
            Use BBC for textual content and Flickr for images / big files
        """
        try:
            urlopen('http://www.google.com')
        except:
            err = r"Sorry the Content Generator uses crawled data \
                    from the internet. \
                    A web connection is required when a profile is first used"
            raise Exception, err

        self.somedata = {
            'shorttexts' : [],
            'mediumtexts' : [],
            'longtexts' : [],
            'urls' : [],
            'images' : [],
            'bigimages' : []
            }
        itemtally = 0
        imagetally = 0
        sectioncount = settings.get('sectioncount',10)         
        foldercount = settings.get('foldercount',5) 
        itemcount = settings.get('itemcount',10)
        imagecount = settings.get('imagecount',5)
        # Make the random content choice from 40% of content total
        # (add 5 for the test content so not < 1)
        itemused = int(0.4 * sectioncount * foldercount * itemcount) + 5
        imageused = int(0.4 * sectioncount * foldercount * imagecount) + 5
        for category in self.feeds:
            if itemtally > itemused:
                break
            feed = self.bbc % category
            self.out.append("Grabbing " + feed)
            data = urlopen(feed).read()
            dom = parseString(data)
            items = dom.getElementsByTagName('item')
            if not items:
                items = dom.getElementsByTagName('entry')

            self.out.append("Found " + str(len(items)) + " items")
            self.out.append("Downloading bbc feed content...")
            for n in items:
                itemtally += 1
                if itemtally > itemused:
                    break
                itemdata = {}
                for option in ['title', 'description', 'link', ]:
                    els = n.getElementsByTagName(option)
                    if len(els) and getattr(els[0], 'firstChild'):
                        itemdata[option] = els[0].firstChild.data

                if 'link' in itemdata:
                    start = """<p class="first">"""
                    end = """<br clear="all" />"""
                    link = itemdata['link'].replace('go/rss/-/', '')
                    # Now try to parse the content that this links to
                    html = urlopen(link).read()
                    html = html[html.find(start):]
                    html = html[:html.find(end)]
                    text = re.sub('<.*?>', '', html)
                    # Clean up the html
                    text = text.replace('\t', ' ')
                    while text.find('  ') > -1:
                        text = text.replace('  ', ' ')
                    text = text.replace('\r', '\n')
                    text = text.replace(' \n', '\n')
                    text = text.replace('\n ', '\n')
                    while text.find('\n\n\n') > -1:
                        text = text.replace('\n\n\n', '\n\n')
                    body = text
                    if len(body)>10:
                        self.somedata['longtexts'].append(body)
                    if 'title' in itemdata:
                        self.somedata['shorttexts'].append(itemdata['title'])
                    if 'description' in itemdata:
                        self.somedata['mediumtexts'].append(
                                                     itemdata['description'])
                    if 'link' in itemdata:
                        self.somedata['urls'].append(itemdata['link'])

        for category in self.ftags:
            if imagetally > imageused:
                break
            feed = self.flickr % category
            self.out.append("Grabbing " + feed)
            data = urlopen(feed).read()
            dom = parseString(data)
            items = dom.getElementsByTagName('item')
            if not items:
                items = dom.getElementsByTagName('entry')
            self.out.append("Found " + str(len(items)) + " items")
            self.out.append("Downloading flickr image content...")
            for n in items:
                imagetally += 1
                if imagetally > imageused:
                    break
                biglinks = n.getElementsByTagName('media:content')
                links = n.getElementsByTagName('media:thumbnail')
                els = n.getElementsByTagName('media:title')
                if len(els) and getattr(els[0], 'firstChild'):
                    title = els[0].firstChild.data
                else:
                    title = ''
                for link in links:
                    self.crawlImage(imgurl=link.getAttribute('url'),
                                    imagekey='images',title=title)
                for link in biglinks:
                    self.crawlImage(imgurl=link.getAttribute('url'),
                                    imagekey='bigimages',title=title)
                    
    def crawlImage(self, imgurl, imagekey, title=''):
        """ Crawl out image and store in local dictionary """
        if not imgurl:
            return
        self.out.append('Downloading ' + imgurl)
        try:
            data = urlopen(imgurl).read()
            if not title:
                title = imgurl.split('/')[-1]
            self.somedata[imagekey].append([StringIO(data), title, ])
        except Exception, e:
            self.out.append("FAILED to download image")
            self.out.append(e)

    def addContent(self, portal, 
                   sectioncount=3, 
                   foldercount=10, 
                   itemcount=10,
                   imagecount=5,
                   bigimagecount=5,
                   profile='intranet'):
        """ Populate the site with folders and content """
        wftool = getToolByName(portal, "portal_workflow")
        supported_types = ['News Item', 'Document', ]
        topfolders = [ x for x in portal.contentValues() 
                       if x.getId() != 'Members' and x.isPrincipiaFolderish ]
        portal.manage_delObjects(ids=[ x.getId() for x in topfolders ])
        links = []
        self.out.append("Creating the folder structure")
        for i in range(1, sectioncount+1):
            fid = profile + str(i)
            portal.invokeFactory(id=fid, type_name='Folder')
            f = getattr(portal, fid)
            f.setTitle('Folder %i' % i)
            wftool.doActionFor(f, 'publish')
            for j in range(1, foldercount+1):
                sfid = 'subfolder%i' % j
                links.append('/'.join([fid,sfid]))
                f.invokeFactory(id=sfid, type_name='Folder')
                sf = getattr(f, sfid)
                sf.setTitle('Subfolder %i' % j)
                if randint(0, 1):
                    wftool.doActionFor(sf, 'publish')
                sf.reindexObject()
                types = [ x for x in sf.getAllowedTypes() 
                          if x.getId() in supported_types ]
                if not types:
                    continue
                for k in range(1, itemcount+1):
                    type_name = choice(types).getId()
                    cid=sf.generateUniqueId(type_name)
                    sf.invokeFactory(id=cid, type_name=type_name)
                    ob = getattr(sf, cid)
                    ob.setTitle(choice(self.somedata['shorttexts']))
                    ob.setDescription(choice(self.somedata['mediumtexts']))
                    body = choice(self.somedata['longtexts'])
                    ob.setText(self.injectLinks('/' + portal.getId() + '/',body,links))

                    if randint(0, 1):
                        wftool.doActionFor(ob, 'publish')

                    ob.reindexObject()
                    links.append('/'.join([fid,sfid,ob.getId()]))

                for k in range(1, imagecount+1):
                    self.createImage(folder=sf,imagekey='images',
                                     title='image' + str(j) + str(k))
                for k in range(1, bigimagecount+1):
                    self.createImage(folder=sf,imagekey='bigimages',
                                     title='image' + str(j) + str(k))                    
            f.reindexObject()

    def injectLinks(self,rooturl,text,links):
        """ Add more realism by adding some links to the body text """
        href = '<a href="' + rooturl
        if links and len(text)>100:
            newtext = text[:80] + href + '%s">' % choice(links)
            newtext += text[80:90] + '</a>' 
            prev = 90
            for i in range(1,5):
                next = i*500
                if len(text) < next + 10:
                    newtext += text[prev:]
                    return newtext
                newtext += text[prev:next]
                newtext += href + '%s">' % choice(links)
                prev = next + 10
                newtext += text[next:prev] + '</a>'
            return newtext + text[prev:]
        else:
            return text

    def createImage(self,folder,imagekey,title):
        """ Add an image to a folder and possibly publish it"""
        img = choice(self.somedata[imagekey])
        cid = folder.generateUniqueId('flickr')                    
        folder.invokeFactory(id=cid, type_name='Image')
        ob = getattr(folder, cid)
        ob.setImage(img[0], content_type="image/jpeg")
        try:
            ob.setTitle(img[1])
        except:
            ob.setTitle(title)


    def getFSPaths(self):
        """ Looks up paths for exporting content to, currently 
            the profile but the egg cache may be a better locale """
        if not getattr(self,'fspaths', None):
            importfolder = os.path.join(INSTANCE_HOME,'import')            
            if INSTANCE_HOME.find('parts'):
                #buildout layout
                exportfolder = INSTANCE_HOME.replace('parts','var') 
            else:
                exportfolder = os.path.join(INSTANCE_HOME,'var')
            self.fspaths = [importfolder, exportfolder]
        return self.fspaths

    def checkZEXP(self, profile, sectioncount):
        """ Checks whether all the content has already 
            been scraped created and exported """
        importfolder, exportfolder = self.getFSPaths()
        for i in range(1, sectioncount+1):
            filename = profile + str(i) + '.zexp'
            srcfile=os.path.join(importfolder,filename)
            if not srcfile or not os.path.exists(srcfile):
                return False
        return True
        
    def cloneContent(self, portal, multiply=2, 
                     sectioncount=3, foldercount=5, profile='intranet'):
        """Clones folders to bulk up content without crawl or zexp import"""
        self.out.append('Cloning content:')
        wftool = getToolByName(portal, "portal_workflow")
        for c in range(1, multiply+1):
            for i in range(1, sectioncount+1):
                foldername = profile + str(i)
                folder = getattr(portal,foldername,None)
                if folder:
                    self.out.append('Cloning folder ' + foldername)
                    cloneid = foldername + 'copy' + str(c)
                    portal.manage_clone(folder, cloneid)
                    clone = getattr(portal,cloneid)
                    if randint(0, 1):
                        wftool.doActionFor(clone, 'publish')
                    for j in range(1, foldercount+1):
                        sfid = 'subfolder%i' % j
                        subfolder = getattr(clone,sfid,None)
                        if subfolder:
                            if randint(0, 1):
                                wftool.doActionFor(subfolder, 'publish')
                            for id in subfolder.objectIds():
                                if not id.startswith('flickr') and randint(0, 1):
                                    obj = getattr(subfolder,id,None)
                                    if obj:
                                        wftool.doActionFor(obj, 'publish')                                    
        return

    def addZEXPContent(self, portal, sectioncount=3, profile='intranet'):
        """Adds in zexps of content generated by the RSS crawl
           Can also be used to add in real content zexps 
           users may want to benchmark"""
        importfolder, exportfolder = self.getFSPaths()
        self.out.append('Adding ZEXP content:')
        for i in range(1, sectioncount+1):
            filename = profile + str(i) + '.zexp'
            srcfile = os.path.join(importfolder,filename)
            portal.manage_importObject(filename, set_owner=0)
        return

    def exportZEXPContent(self, portal, sectioncount=3, profile='intranet'):
        """Exports all the top level folders in a site - 
           really a zopectl utility method"""
        importfolder, exportfolder = self.getFSPaths()
        self.out.append('Exporting ZEXP content:')
        for i in range(1, sectioncount+1):
            foldername = profile + str(i)
            item = getattr(portal,foldername, None)
            if item and item.isPrincipiaFolderish:
                try:
                    portal.manage_exportObject(foldername)
                    srcfile=os.path.join(exportfolder,foldername + '.zexp')
                    shutil.copy(srcfile,importfolder)
                    self.out.append('Exported zexp of ' + foldername)
                except:
                   self.out.append('Export of ' + foldername + ' failed')
        return

InitializeClass(ContentSetup)

