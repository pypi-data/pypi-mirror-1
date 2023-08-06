from django.conf import settings
execfile(settings.PLATFORM_ROOT + '/core_website/test/urls.py')
testurl('home')
testurl('/property/find/?type=residentialproperty&lat=-28.643387&lng=153.612224&scale=4&page=1&perpage=10&min_price=&max_price=&has_pool=0&has_spa=0&heating=&bedrooms=&bathrooms=')
testurl('/property/find/?type=rentalproperty&lat=-28.643387&lng=153.612224&scale=4&page=1&perpage=10&min_price=&max_price=&has_pool=0&has_spa=0&heating=&bedrooms=&bathrooms=')
testurl('/asfds33')
testurl('badpage')
