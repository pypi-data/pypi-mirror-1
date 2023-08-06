from django.conf import settings
#from satchmo_store.urls import urlpatterns
from django.conf.urls.defaults import *
import property.views
#import website.default_urls
#from django.conf.urls.defaults import *

#from satchmo_store.urls import urlpatterns
#urlpatterns += patterns('',
#    (r'^tribes/', include('subscriptiontribes.urls')),
#    (r'^schedule/', include('schedule.urls')),
#)

urlpatterns = patterns('',
    url(r'^$', property.views.homepage, name="home"),
    )
execfile(settings.PLATFORM_ROOT + '/core_website/default_urls.py')


