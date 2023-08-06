from django.conf import settings
from django.test import Client
from django.test.utils import setup_test_environment
import re

import logging
log = logging.getLogger('testmaker')
print "Loaded Testmaker Middleware"

class TestMakerMiddleware(object):
   def process_request(self, request):
       if request.method == 'POST' and 'test_client_true' not in request.POST\
                          and not re.search("admin", request.path): #So admin works
           post_str =  "'" + request.path + "', {"
           for arg in request.POST:
               post_str +=  "'" + arg + "': '" + request.POST[arg] + "',"
           post_str += "}"
           log.info("r = c.post(" + post_str + ")")

       if request.method == 'GET' \
                          and 'test_client_true' not in request.GET \
                          and not re.search("admin", request.path): #So admin works
           setup_test_environment()
           c = Client()
           get_str =  "'%s', {" % request.path
           for arg in request.GET:
               get_str +=  "'%s': '%s'," % (arg, request.GET[arg])
           get_str += "}"
           log.info("\t\tr = c.get(%s)" % get_str)
           getdict = request.GET.copy()
           getdict['test_client_true'] = 'yes'
           r = c.get(request.path, getdict)
           try:
               log.info("\t\tself.assertEqual(r.status_code, %s)" % r.status_code)
               con = r.context[-1].dicts[-1]
               if con == {}:
                  con = r.context[-1].dicts[0]
               if 'MEDIA_URL' in con:
                  con = {}
               for var in con:
                   if not re.search("0x\w+", unicode(con[var])):
                     log.info(u"\t\tself.assertEqual(unicode(r.context[-1]['%s']), '%s')" % (var, unicode(con[var])) )
           except ( KeyError, TypeError, IndexError), err:
               #log.error("Error in Get try block: " + str(err))
               pass
