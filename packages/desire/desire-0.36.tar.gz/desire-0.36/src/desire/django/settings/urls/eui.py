from django.conf.urls.defaults import *
import re
import desire.regexps

urlpatterns = patterns('desire.django.apps.eui.views',

    #   Remote Procedure Call
    ##
    
    (r'^rpc/(?P<viewName>(.*))/$',
        'rpc.view'),

    (r'^autocomplete/$',
        'rpc.autocomplete'),

    (r'^autoappend/$',
        'rpc.autoappend'),

    (r'^autodelete/$',
        'rpc.autodelete'),
    
    (r'^attrupdate/$',
        'rpc.attrupdate'),


    #
    ##  Application Home Page

    (r'^$',
        'welcome.welcome'),

    #
    ##  Help Page

    (r'^help/$',
        'welcome.welcome'),

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
    
    #(r'^registry/$',
    #    'welcome.registry'),

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

    (r'^persons/(?P<personName>%s)/$' % desire.regexps.personName,
        'person.read'),

    (r'^persons/(?P<personName>%s)/home/$' % desire.regexps.personName,
        'person.read'),

    (r'^persons/(?P<personName>%s)/update/$' % desire.regexps.personName,
        'person.update'),

    (r'^persons/(?P<personName>%s)/delete/$' % desire.regexps.personName,
        'person.delete'),

    (r'^persons/(?P<personName>%s)/approve/$' % desire.regexps.personName,
        'person.approve'),

    #
    ## Registry views

    (r'^(?P<registryPath>(walks|collections|processes|goals|stories|events|requirements|products).*)/(?P<actionName>(find))/(?P<actionValue>[\w\d]*)/$',
        'registry.view'),

    (r'^(?P<registryPath>(walks|collections|processes|goals|stories|events|requirements|products).*)/(?P<actionName>(create|update|delete|read|search|undelete|purge))/$',
        'registry.view'),

    (r'^(?P<registryPath>(walks|collections|processes|goals|stories|events|requirements|products).*)/$',
        'registry.view'),

    #
    ## Specialized views



    #
    ##  Not Found
   
    (r'^.*$',
        'welcome.pageNotFound'),
)

