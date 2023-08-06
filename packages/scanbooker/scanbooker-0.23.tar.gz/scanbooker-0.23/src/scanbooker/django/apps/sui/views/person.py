from dm.view.base import *
from scanbooker.django.apps.sui.views.base import ScanBookerView
from scanbooker.django.apps.sui.views import manipulator
import scanbooker.command
from dm.exceptions import KforgeCommandError
import random
from scanbooker.dictionarywords import AC_SKIP_ROLE_INFERENCE

class PersonView(ScanBookerView, AbstractClassView):

    domainClassName = 'Person'
    majorNavigationItem = '/persons/'
    minorNavigationItem = '/persons/'

    def isViewerAdministrator(self):
        if self.session and self.session.person and self.session.person.role:
            if self.session.person.role.name == "Administrator":
                return True
        return False
        
    def __init__(self, **kwds):
        super(PersonView, self).__init__(**kwds)
        self.person = None

    def setMinorNavigationItems(self):
        self.minorNavigation = []
        if self.canReadPersons():
            self.minorNavigation.append(
                {
                    'title': 'Index', 
                    'url': '/persons/'
                }
            )
            self.minorNavigation.append(
                {
                    'title': 'Search',
                    'url': '/persons/search/'
                }
            )
        person = self.getDomainObject()
        if not person:
            if self.session and self.session.person:
                person = self.session.person
        if person and self.session:
            self.minorNavigation.append(
                {
                    'title': 'Home',
                    'url': '/persons/%s/' % person.name
                }
            )
            if person.state.name == "pending":
                if self.canApprovePerson():
                    self.minorNavigation.append(
                        {
                            'title': 'Approve', 
                            'url': '/persons/%s/approve/' % person.name
                        }
                    )
            else:
                if self.canUpdatePerson():
                    self.minorNavigation.append(
                        {
                            'title': 'Update', 
                            'url': '/persons/%s/update/' % person.name
                        }
                    )
        if not self.session:
            self.minorNavigation.append(
                {
                    'title': 'Log in', 
                    'url': '/login/'
                }
            )
            if self.canCreatePerson():
                self.minorNavigation.append(
                    {
                        'title': 'Register', 
                        'url': '/persons/create/'
                    }
                )

    def setContext(self):
        super(PersonView, self).setContext()
        isRoleInference = not self.dictionary[AC_SKIP_ROLE_INFERENCE]
        self.context.update({
            'person'         : self.getDomainObject(),
            'canUpdatePerson': self.canDeletePerson(),
            'canDeletePerson': self.canUpdatePerson(),
            'isRoleInference': isRoleInference,
            'registryPath': 'persons',
            'registerName': 'users',
            'registerNameTitle': 'Registration',
            'domainClassName': 'User',
        })

    def getDomainObject(self):
        super(PersonView, self).getDomainObject()
        self.person = self.domainObject
        return self.person

    def isSessionPerson(self):
        if self.session and self.domainObject:
            return self.session.person == self.domainObject
        else:
            return False

    def saveSafetyTrainingCertificate(self, researcher):
        if not researcher:
            return
        requestParams = self.getRequestParams()
        if not self.request.FILES.has_key('safetyTrainingCertificate'):
            return
        uploadFile = self.request.FILES['safetyTrainingCertificate']
        if not uploadFile:
            return
        # todo: Protection aganist bad uploadFile dict.
        content = uploadFile['content']
        contentType = uploadFile['content-type']
        certificate = self.registry.safetyTrainingCertificates.create(
            researcher=self.domainObject.researcher,
            contentType=contentType,
        )
        certificate.file = content
        certificate.save()

    def canCreateDomainObject(self):
        return self.canCreatePerson()

    def canUpdateDomainObject(self):
        return self.canUpdatePerson()

    def canDeleteDomainObject(self):
        return self.canDeletePerson()



class PersonListView(PersonView, AbstractListView):

    templatePath = 'persons/list'
    minorNavigationItem = '/persons/'

    def canAccess(self):
        return self.canReadPerson()


class PersonSearchView(PersonView, AbstractSearchView):

    templatePath = 'persons/search'
    minorNavigationItem = '/persons/search/'
    
    def canAccess(self):
        return self.canReadPerson()


class PersonCreateView(PersonView, AbstractCreateView):

    templatePath = 'persons/create'
    minorNavigationItem = '/persons/create/'

    def getManipulatorClass(self):
        return manipulator.PersonCreateManipulator

    def canAccess(self):
        return self.canCreatePerson()
        
    def getInitialParams(self):
        initialParams = super(PersonCreateView, self).getInitialParams()
        initialParams['requestedRole'] = 'Researcher'
        return initialParams

    def getCreateParams(self):
        createParams = self.getRequestParams()
        if createParams.has_key('safetyTrainingCertificate'):
            del(createParams['safetyTrainingCertificate'])
        return createParams

    def manipulateDomainObject(self):
        super(PersonCreateView, self).manipulateDomainObject()
        if self.domainObject:
            person = self.domainObject
            initials = "".join(
                [i[0] for i in person.fullname.replace("-", " ").split(" ")]
            ).upper()
            pendingResearchers = self.registry.researchers.getPending()
            person.researcher = pendingResearchers.create(
                realname=person.fullname, initials=initials
            )
            person.save()
            self.saveSafetyTrainingCertificate(person.researcher)
        #self.approveIfCanApprove()

    def approveIfCanApprove(self):
        person = self.getManipulatedDomainObject()
        if person and self.canApprovePerson():
            person.approve()
            
    def setContext(self):
        super(PersonCreateView, self).setContext()
        if self.dictionary['captcha.enable']:
            captchaHash = self.captcha.name
            captchaUrl = self.makeCaptchaUrl(captchaHash)
            self.context.update({
                'isCaptchaEnabled'  : True,
                'captchaHash'       : captchaHash,
                'captchaUrl'        : captchaUrl,
            })
        else:
            self.context.update({
                'isCaptchaEnabled'  : False,
            })

    def makePostManipulateLocation(self):
        person = self.getDomainObject()
        if person:
            if person.state.name == "active" and self.canReadPerson():
                return '/persons/%s/' % person.name
            elif person.state.name == "pending" and self.canApprovePerson():
                return '/persons/%s/approve/' % person.name
        return ''


class PersonPendingView(PersonView, AbstractPendingView):

    templatePath = 'persons/pending'
    minorNavigationItem = '/persons/pending/'

    def canAccess(self):
        return self.canUpdatePerson()

# todo: returnPath support
# todo: captcha support


#    def makeForm(self):
#        if self.dictionary['captcha.enable']:
#            if self.requestParams.get('captchahash', False):
#                hash = self.requestParams['captchahash']
#                try:
#                    self.captcha = self.registry.captchas[hash]
#                except:
#                    self.makeCaptcha()
#                    self.requestParams['captchahash'] = self.captcha.name
#                    self.requestParams['captcha'] = ''
#            else:
#                self.makeCaptcha()
#                self.requestParams['captchahash'] = self.captcha.name
#                self.requestParams['captcha'] = ''
#                
#        self.form = manipulator.FormWrapper(
#            self.manipulator, self.requestParams, self.formErrors
#        )
#
#    # todo: delete old and deleted captchas, and their image files - cron job?
#
#    def makeCaptcha(self):
#        word = self.makeCaptchaWord()
#        hash = self.makeCaptchaHash(word)
#        try:
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        except:
#            hash = self.makeCaptchaHash(word)
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        
#        fontPath = self.dictionary['captcha.font_path']
#        if not fontPath:  # todo: instead, check file exists
#            raise Exception("No 'captcha.font_path' in system dictionary.")
#        fontSize = int(self.dictionary['captcha.font_size'])
#        path = self.makeCaptchaPath(hash)
#        import kforge.utils.captcha
#        kforge.utils.captcha.gen_captcha(word, fontPath, fontSize, path)
#
#    def makeCaptchaWord(self):
#        wordlength = 5
#        word = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ', wordlength))
#        return word
#
#    def makeCaptchaHash(self, word):
#        return self.makeCheckString(word)
#
#    def makeCaptchaPath(self, captchaHash):
#        mediaRoot = self.dictionary['www.media_root']
#        captchaRoot = mediaRoot + '/images/captchas'
#        captchaPath = captchaRoot + '/%s.png' % captchaHash
#        return captchaPath
#
#    def makeCaptchaUrl(self, captchaHash):
#        mediaHost = self.dictionary['www.media_host']
#        mediaPort = self.dictionary['www.media_port']
#        captchaUrl = 'http://%s:%s/images/captchas/%s.png' % (
#            mediaHost,
#            mediaPort,
#            captchaHash,
#        )
#        return captchaUrl
#
#    def createPerson(self):
#        personName = self.requestParams.get('name', '')
#        command = kforge.command.PersonCreate(personName)
#        try:
#            command.execute()
#        except:
#            # todo: log error
#            self.person = None
#            return None
#        else:
#            command.person.fullname = self.requestParams.get('fullname', '')
#            command.person.email = self.requestParams.get('email', '')
#            command.person.setPassword(self.requestParams.get('password', ''))
#            command.person.save()
#            self.person = command.person
#        return self.person


class PersonReadView(PersonView, AbstractReadView):

    templatePath = 'persons/read'
    majorNavigationItem = '/persons/'

    def getMinorNavigationItem(self):
        return '/persons/%s/' % self.getDomainObject().name

    def getDomainObject(self):
        super(PersonReadView, self).getDomainObject()
        if not self.domainObject:
            if self.session:
                self.domainObject = self.session.person
        return self.domainObject

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canReadPerson()

    def setContext(self):
        super(PersonReadView, self).setContext()
        self.context.update({
            'isSessionPerson': self.isSessionPerson()
        })


class PersonUpdateView(PersonView, AbstractUpdateView):

    templatePath = 'persons/update'
    majorNavigationItem = '/persons/home/'

    def getMinorNavigationItem(self):
        return '/persons/%s/update/' % self.getDomainObject().name

    def getManipulatorClass(self):
        if self.isViewerAdministrator():
            return manipulator.PersonUpdateManipulatorAdmin
        else:
            return manipulator.PersonUpdateManipulator

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canUpdatePerson()

    def manipulateDomainObject(self):
        super(PersonUpdateView, self).manipulateDomainObject()
        if self.domainObject:
            person = self.domainObject
            self.saveSafetyTrainingCertificate(person.researcher)
        
    def getUpdateParams(self):
        updateParams = self.getRequestParams()
        if updateParams.has_key('safetyTrainingCertificate'):
            del(updateParams['safetyTrainingCertificate'])
        return updateParams

    def makePostManipulateLocation(self):
        person = self.getDomainObject()
        personKey = self.registry.persons.getRegisterKey(person)
        return '/persons/%s/' % personKey


class PersonDeleteView(PersonView, AbstractDeleteView):

    templatePath = 'persons/delete'
    
    def getMinorNavigationItem(self):
        return '/persons/%s/delete/' % self.getDomainObject().name

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canDeletePerson()

    def manipulateDomainObject(self):
        super(PersonDeleteView, self).manipulateDomainObject()
        person = self.getDomainObject()
        if person and self.session and self.session.person:
            if person == self.session.person:
                self.stopSession()

    def makePostManipulateLocation(self):
        return '/persons/'


class PersonApproveView(PersonView, AbstractApproveView):

    templatePath = 'persons/approve'
    
    def getMinorNavigationItem(self):
        return '/persons/%s/approve/' % self.getDomainObject().name

    def getManipulatorClass(self):
        return manipulator.PersonApproveManipulator
    
    def canAccess(self):
        return self.canApprovePerson()

    #def getInitialParams(self):
    #    initialParams = super(PersonApproveView, self).getInitialParams()
    #    initialParams['createresearcher'] = True
    #    return initialParams

    def manipulateDomainObject(self):
        super(PersonApproveView, self).manipulateDomainObject()
        self.approveLinkedResearcher()

    def approveLinkedResearcher(self):
        person = self.getManipulatedDomainObject()
        person.researcher.approve()
        requestedGroup = person.requestedGroup
        if person.requestedRole.name == "PrincipalInvestigator":
            if requestedGroup:
                person.researcher.principalships.create(requestedGroup)
            else:
                group = self.registry.groups.create(
                    title=person.researcher.realname
                )
                person.researcher.principalships.create(group)
        elif person.requestedRole.name == "Researcher":
            if requestedGroup:
                person.researcher.memberships.create(requestedGroup)

    def makePostManipulateLocation(self):
        person = self.getDomainObject()
        personKey = self.registry.persons.getRegisterKey(person)
        return '/persons/%s/' % personKey


def list(request):
    view = PersonListView(request=request)
    return view.getResponse()
    
def search(request, startsWith=''):
    view = PersonSearchView(request=request, startsWith=startsWith)
    return view.getResponse()
    
def create(request, returnPath=''):   
    view = PersonCreateView(request=request)
    return view.getResponse()

def pending(request, returnPath=''):   
    view = PersonPendingView(request=request)
    return view.getResponse()

def read(request, personName=''):
    view = PersonReadView(request=request, domainObjectKey=personName)
    return view.getResponse()

def update(request, personName):
    view = PersonUpdateView(request=request, domainObjectKey=personName)
    return view.getResponse()

def delete(request, personName):
    view = PersonDeleteView(request=request, domainObjectKey=personName)
    return view.getResponse()

def approve(request, personName):
    view = PersonApproveView(request=request, domainObjectKey=personName)
    return view.getResponse()

