import dm.plugin.base
import os

import dm.util.mailer
from dm.dictionarywords import *

class Plugin(dm.plugin.base.PluginBase):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)

    def onPersonCreate(self, person):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        pending = self.registry.states['pending']
        # todo: change this so if pending send email
        # todo: set state on the create view
        person.state = pending
        person.save()
        msg = 'Person registration pending: %s' % person.name
        msg += '\n\n'
        msg += 'http://'+self.dictionary[DOMAIN_NAME]
        if self.dictionary[HTTP_PORT] != '80':
            msg += ':'+self.dictionary[HTTP_PORT]
        msg += self.dictionary[URI_PREFIX]+'/persons/'+person.name+'/approve/'
        self.notifySystemAdmins(msg)

    def onSafetyTrainingCertificateCreate(self, certificate):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        msg = 'New safety training certificate uploaded'
        msg += '\n\n'
        msg += 'http://'+self.dictionary[DOMAIN_NAME]
        if self.dictionary[HTTP_PORT] != '80':
            msg += ':'+self.dictionary[HTTP_PORT]
        msg += self.dictionary[URI_PREFIX]
        msg += '/certificates/%s/' % certificate.id
        msg += '\n\n'
        person = certificate.getPerson()
        personName = person and person.name or ''
        if personName:
            msg += 'http://'+self.dictionary[DOMAIN_NAME]
            if self.dictionary[HTTP_PORT] != '80':
                msg += ':'+self.dictionary[HTTP_PORT]
            msg += self.dictionary[URI_PREFIX]
            msg += '/persons/%s/' % personName
        msg += '\n\n'
        self.notifySystemAdmins(msg)

    def notifySystemAdmins(self, msg):
        admins = self.getSystemAdmins()
        self.notifyPersons(msg, admins)

    def getSystemAdmins(self):
        admin = self.registry.roles['Administrator']
        return self.registry.persons.findDomainObjects(role=admin)

    def notifyPersons(self, message, persons):
        self.notifyPersonsByEmail(message, persons)
    
    def notifyPersonsByEmail(self, message, persons):
        systemName = self.dictionary[SYSTEM_NAME]
        domainName = self.dictionary[DOMAIN_NAME]
        subject = 'Changes to %s' % systemName
        sender = 'scanbooker-noreply@' + domainName
        recipients = []
        for person in persons:
            if person and person.email:
                recipients.append(person.email)
        logmsg = 'Registration Plugin: sending email to %s' % recipients
        self.log(logmsg)
        self.sendEmail(sender, recipients, subject, message)

    def sendEmail(self, sender, recipients, subject, message):
        if not recipients:
            self.log('Registration Plugin: Not sending email: no recipients.')
            return
        if self.dictionary[SKIP_EMAIL_SENDING]:
            self.log('Registration Plugin: Skipping sending email.')
            return
        try:
            if not self.dictionary[SKIP_EMAIL_SENDING]:
                dm.util.mailer.send(
                    from_address=sender,
                    to_addresses=recipients, 
                    subject=subject,
                    body=message
                )
        except Exception, inst:
            # TODO: make this more Exception specific
            # will get an exception if e.g. one of recipients does not exist 
            # since raising an exception will stop whatever action is taking
            # place which led to this notification being raised (e.g. project
            # creation and deletion) let us just log the error
            msg = 'Registration Plugin: sending mail failed. Exception info: %s' % inst
            self.log(msg)



