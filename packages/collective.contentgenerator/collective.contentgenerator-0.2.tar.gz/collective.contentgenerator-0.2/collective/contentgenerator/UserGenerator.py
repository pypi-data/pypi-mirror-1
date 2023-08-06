from Globals import INSTANCE_HOME, InitializeClass
from Products.CMFCore.utils import getToolByName
import random

class UserSetup:
    """ Creates a set of users and groups, then adds users to groups 
        and local roles on content to groups for the first and 
        second level if roles is flagged """

    def __init__(self):
        self.out = []
            
        self.forenames = ['Alex','Ben','Cath','Daniel','Eli','Freddy',
                          'Gwen','Herbie','Ivan','Jay','Kiash',
                          'Len','Max','Nobby','Oscar','Phil','Quentin',
                          'Rachel','Sophie','Toby','Una','Victor',
                          'Wendy','Xen','Yvonne','Zachary']
        self.surnames = ['Anderson','Barnes','Crewe','Douglas',
                         'Emmins','Farquar','Gaskill','Hughes','Illiad',
                         'Jones','Kash','Lyons','Moon','Norman','Order',
                         'Paul','Quail','Robert','Simon','Timms',
                         'Underhill','Vernon','Wally','Xavier','Zeb']
        self.groups = ['ant','bee','cat','dog','elephant','fish',
                       'goat','hippo','insect','jackdaw','kangaroo',
                       'lion','monkey','newt','ostrich','penguin',
                       'quail','rabbit','snake','tiger','uakari','vole',
                       'whale','xiphias','yak','zebra']
        self.az = 'abcdefghijklmnopqrstuvwxyz'
        self.role = ['Contributor','Editor','Reader','Reviewer','Manager']
        self.groupid = []
        self.grouptitle = []
        self.fullname = []
        self.userid = []
        self.ucount = 0
        self.gcount = 0

    def customize(self, portal, context, settings={}, logging='log'):
        """ Run the portal customisation methods that dds users and groups """
        self.out = []
        self.generateUsers(settings.get('users',100))
        self.createUsers(portal)
        self.generateGroups(settings.get('groups',10))
        self.createGroups(portal,
                          settings.get('memberships',10),
                          settings.get('local',False))
        
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

    def generateGroups(self,groups=0):
        """ Generates groupdata for up to 17000 groups """
        if groups>17500:
            groups = 17500
        self.gcount = 0
        self.groupid = []
        self.grouptitle = []
        for firstletter in self.az:
            if self.gcount == groups:
                break
            for secondletter in self.az:
                if self.gcount == groups:
                    break
                for group in self.groups:
                    if self.gcount == groups:
                        break
                    letterid = firstletter + secondletter
                    self.groupid.append(group + letterid)
                    self.grouptitle.append(group + ' group section ' + letterid)
                    self.gcount += 1
                    
    def createGroups(self, portal,memberships=0,local=False):
        """ Create real groups in the portal from the generated group data 
            - and adds local roles if local flagged
        """
        grp_tool = getToolByName(portal,'portal_groups')
        mem_tool = getToolByName(portal,'portal_membership')
        grp_tool.toggleGroupWorkspacesCreation()

        for i in range(self.gcount):
            grp_tool.addGroup(self.groupid[i],'',(),())
	    created_group=grp_tool.getGroupById(self.groupid[i])
	    created_group.setGroupProperties({'title':self.grouptitle[i]})

        random.seed()

        # Add 5 local roles per folder
        if local:
            for j in range(5):
                for item in portal.objectValues():
                    if item.isPrincipiaFolderish:
                        for subitem in item.objectValues():
                            if subitem.isPrincipiaFolderish:
                                mem_tool.setLocalRoles(
                                    obj=subitem,
                                    member_ids=(random.choice(self.groupid),),
                                    member_role=random.choice(self.role)
                                    )

        users = len(self.userid) - 1
        for i in range(users):
            for j in range(memberships):
                groupid = random.choice(self.groupid)
                created_group = grp_tool.getGroupById(groupid)
                if created_group:
                    created_group.addMember(self.userid[i])

    def generateUsers(self,users=0):
        """ Generates user data for up to 17000 users """
        if users>17500:
            users = 17500
        self.ucount = 0
        self.fullname = []
        self.userid = []
        for fname in self.forenames:
            if self.ucount == users:
                break
            for mname in self.forenames:
                if self.ucount == users:
                    break
                for sname in self.surnames:
                    if self.ucount == users:
                        break
                    self.fullname.append(fname + ' ' + mname + ' ' + sname)
                    self.userid.append(fname[0].lower() 
                                    + mname[0].lower() + sname.lower())
                    self.ucount += 1

    def createUsers(self, portal):
        """ Create real users in the portal from the generated user data 
            - by default in Simple User Folder
        """
        grp_tool = getToolByName(portal,'portal_groups')
        reg_tool = getToolByName(portal,'portal_registration')
        for i in range(self.ucount):
            reg_tool.addMember(self.userid[i], 
                               'testpw', 
                               properties={
                                  'email':self.userid[i] + '@test.plone.org',
                                  'fullname':self.fullname[i], 
                                  'username':self.userid[i]
                                })


InitializeClass(UserSetup)
