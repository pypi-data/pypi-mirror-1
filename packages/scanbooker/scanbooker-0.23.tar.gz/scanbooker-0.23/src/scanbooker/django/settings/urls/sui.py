from django.conf.urls.defaults import *
import re
import scanbooker.regexps


# Todo: Remove old schedule view code.

urlpatterns = patterns('scanbooker.django.apps.sui.views',

    #   Remote Procedure Call
    ##
    
    (r'^rpc2/(?P<viewName>(.*))/$',
        'rpc2.view'),

    (r'^rpc/(?P<viewName>(.*))/$',
        'rpc.view'),

    #
    ##  Application Home Page

    (r'^$',
        'schedule.view2'),

    #
    ##  Help Page

    (r'^help/$',
        'welcome.welcome'),

    #
    ##  My Space

    (r'^myspace/$',
        'myspace.myspace'),

    #
    ##  User Authentication

    (r'^login/(?P<returnPath>(.*))$',
        'accesscontrol.login'),
        
    (r'^logout(?P<redirect>(.+))$',
        'accesscontrol.logout'),

    (r'^persons/home/$',
        'welcome.user'),

    #
    ##  Access Control
    
    (r'^accessDenied/(?P<deniedPath>(.*))$',
        'welcome.accessDenied'),

    #
    ##  Administration
    
    (r'^admin/model/create/(?P<className>(\w*))/$',
        'admin.create'),

    (r'^admin/model/update/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.update'),

    (r'^admin/model/delete/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.delete'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.listHasMany'),

    (r'^admin/model/create/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.createHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.readHasMany'),

    (r'^admin/model/update/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.updateHasMany'),

    (r'^admin/model/delete/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.deleteHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/$',
        'admin.read'),

    (r'^admin/model/(?P<className>([^/]*))/$',
        'admin.list'),

    (r'^admin/model/$',
        'admin.model'),

    (r'^admin/$',
        'admin.index'),


    #
    ##  Registry Welcome
    
    (r'^registry/$',
        'welcome.registry'),

    #
    ##  Certificates
    
    (r'^certificates/(?P<certificateId>[\d]*)/$',
        'image.read'),

    #
    ##  Person

    (r'^persons/create/(?P<returnPath>(.*))$',
        'person.create'),

    (r'^persons/pending/$',
        'person.pending'),

    (r'^persons/$',
        'person.list'),

    (r'^persons/find/(?P<startsWith>[\w\d]+)/$',
        'person.search'),

    (r'^persons/find/$',
        'person.search'),

    (r'^persons/search/$',
        'person.search'),

    (r'^persons/home/$',
        'person.read'),

    (r'^persons/(?P<personName>%s)/$' % scanbooker.regexps.personName,
        'person.read'),

    (r'^persons/(?P<personName>%s)/home/$' % scanbooker.regexps.personName,
        'person.read'),

    (r'^persons/(?P<personName>%s)/update/$' % scanbooker.regexps.personName,
        'person.update'),

    (r'^persons/(?P<personName>%s)/delete/$' % scanbooker.regexps.personName,
        'person.delete'),

    (r'^persons/(?P<personName>%s)/approve/$' % scanbooker.regexps.personName,
        'person.approve'),

    #
    ##  Volunteer Booking

    (r'^volunteers/booking/$',
        'volunteer.booking'),

    (r'^volunteers/booking/(?P<volunteerId>\d+)/$',
        'volunteer.booking'),

    (r'^volunteers/booking/(?P<volunteerId>\d+)/(?P<sessionId>\d+)/$',
        'volunteer.booking'),

    (r'^volunteers/booking/(?P<volunteerId>\d+)/(?P<sessionId>\d+)/(?P<isConfirmed>\w+)/$',
        'volunteer.booking'),

    (r'^volunteers/cancellation/$',
        'volunteer.cancellation'),

    (r'^volunteers/cancellation/(?P<volunteerId>\d+)/$',
        'volunteer.cancellation'),

    (r'^volunteers/cancellation/(?P<volunteerId>\d+)/(?P<sessionId>\d+)/$',
        'volunteer.cancellation'),

    (r'^volunteers/cancellation/(?P<volunteerId>\d+)/(?P<sessionId>\d+)/(?P<isConfirmed>\w+)/$',
        'volunteer.cancellation'),

    (r'^volunteers/hitlist/$',
        'volunteer.hitlist'),

    (r'^volunteers/hitlist/(?P<volunteerId>\d+)/(?P<actionName>\w+)/$',
        'volunteer.hitlist'),

    #
    ##  Registry View 

    (r'^(?P<registryPath>(earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions).*)/earlier/$',
        'registryExtn.earlier'),

    (r'^(?P<registryPath>(earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions).*)/later/$',
        'registryExtn.later'),

    (r'^(?P<registryPath>(earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions).*)/shorten/$',
        'registryExtn.shorten'),

    (r'^(?P<registryPath>(earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions).*)/lengthen/$',
        'registryExtn.lengthen'),

    (r'^(?P<registryPath>(earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions).*)/ends/(?P<timeBlockName>\d\d\d\d)/$',
        'registryExtn.ends'),

    (r'^updatepost2/(?P<registryPath>(earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions).*)/update/$',
        'rpc2.updatepost'),

    (r'^updatepost/(?P<registryPath>(earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions).*)/update/$',
        'rpc.updatepost'),

    (r'^(?P<registryPath>(scanners|researchers|radiographers|organisations|groups|volunteers|approvals|projects|fundingStatuses|earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions|trainingSessions|weekEarmarkTemplates|earmarkedTimeTemplateWeeks|reports|accounts).*)/(?P<actionName>(find))/(?P<actionValue>[\w\d]*)/$',
        'registry.view'),

    (r'^(?P<registryPath>(scanners|researchers|radiographers|organisations|groups|volunteers|approvals|projects|fundingStatuses|earmarkedTimes|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions|trainingSessions|weekEarmarkTemplates|earmarkedTimeTemplateWeeks|reports|accounts).*)/(?P<actionName>(create|update|delete|read|search|undelete|purge|listall))/$',
        'registry.view'),

    (r'^(?P<registryPath>(scanners|researchers|radiographers|organisations|groups|volunteers|approvals|projects|fundingStatuses|earmarkedTimes|earmarkedTimeTemplateWeeks|maintenanceSessions|methodsSessions|scanningSessions|downtimeSessions|trainingSessions|weekEarmarkTemplates|reports|accounts).*)/$',
        'registry.view'),
 
    #
    #  Schedule 2 View

    (r'^schedule2/$',
        'schedule.view2'),

    #
    #  Schedule View

    (r'^schedule/$',
        'schedule.view2'),

    (r'^schedule/year/$',
        'schedule.view2'),

    (r'^schedule/month/$',
        'schedule.view2'),

    (r'^schedule/week/$',
        'schedule.view2'),

    (r'^schedule/day/$',
        'schedule.view2'),

    (r'^schedule/year/(?P<year>\d*)/(?P<month>\d*)/(?P<day>\d*)/$',
        'schedule.view2'),

    (r'^schedule/month/(?P<year>\d*)/(?P<month>\d*)/(?P<day>\d*)/$',
        'schedule.view2'),

    (r'^schedule/week/(?P<year>\d*)/(?P<month>\d*)/(?P<day>\d*)/$',
        'schedule.view2'),

    (r'^schedule/day/(?P<year>\d*)/(?P<month>\d*)/(?P<day>\d*)/$',
        'schedule.view2'),

    (r'^schedule/create/$',
        'schedule.create'),

    (r'^schedule/create/(?P<year>\d*)/(?P<month>\d*)/(?P<day>\d*)/(?P<block>\d*)/$',
        'schedule.create'),

    (r'^settings/$',
        'settings.update'),

    #
    ##  Not Found
   
    (r'^.*$',
        'welcome.pageNotFound'),
)

