from django.core.management.base import BaseCommand
from optparse import make_option
import sys, logging, os
from os import path
from django.db.models import get_model, get_models, get_app
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField
from django.core import serializers


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-a', '--app', action='store', dest='application',
            default="all", help='The name of the application (in the current \
                    directory) to output data to. (defaults to currect directory)'),

        make_option('-l', '--logdir', action='store', dest='logdirectory',
            default=os.getcwd(), help='Directory to send tests and fixtures to. \
            (defaults to currect directory)'),

        make_option('-v', '--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),

        make_option('-f', '--fixture', action='store_true', dest='fixture', default=True,
            help='Pass -f to not create a fixture for the data.'),

        make_option('-u', '--unittest', action='store_true', dest='unittest',
            help='Pass -u to create unit tests instead of doctests.'),
    )

    help = 'Runs the test server with the testmaker output enabled'
    args = '[server:port]'

    def handle(self, addrport='', *args, **options):
        from django.conf import settings
        from django.core.management import call_command
        app = options.get("application")
        verbosity = int(options.get('verbosity', 1))
        create_fixtures = options.get('fixture', True)
        logdir = options.get('logdirectory')

        #defaults
        fixturefile = path.join(logdir, app + '-testmaker.json')
        logfile = path.join(logdir, 'tests-testmaker.py')

        #figure out where to put log file and what to call it
        if app != "all" and path.isdir(path.join(logdir, app)):
            logdir = path.join(logdir, app)
            #if tests/ exists, log there
            if path.isdir(path.join(logdir, 'tests')):
                logfile = path.join(logdir, 'tests', 'testmaker-log.py')
            elif path.isfile(path.join(logdir, 'tests.py')):
                logfile = path.join(logdir, 'tests-testmaker.py')
            else:
                logfile = path.join(logdir, 'tests.py')

            #create fixtures directory if needed
            if not path.isdir(path.join(logdir, 'fixtures')):
                os.mkdir(path.join(logdir, 'fixtures'))
            fixturefile = path.join(logdir, 'fixtures',app + '.json')
            if path.exists(fixturefile):
                fixturefile = path.join(logdir, 'fixtures', app + '-testmaker.json')
            if path.exists(fixturefile):
                create_fixtures = False
                if verbosity > 0:
                    print "Not creating fixtures because they seem to already exist"

        if verbosity > 0:
            print "Logging to: " + logfile
            if create_fixtures:
                print "Logging fixtures at " + fixturefile
                #sys.stdout = open(fixturefile, 'w')
                #call_command('dumpdata')
                #sys.stdout = sys.__stdout__

        logging.basicConfig(level=logging.INFO,
                   format='%(message)s',
                   filename= logfile,
                   filemode='w'
                   )

        logging.info('from django.test import TestCase')
        logging.info('from django.test import Client')
        logging.info('c = Client()')
        logging.info('class Testmaker(TestCase):')
        logging.info('\tfixtures = ["%s"]' % fixturefile)
        logging.info('\tdef testcase1(self): ')

        if verbosity > 0:
            print "Starting TestMaker logging server..."
        settings.MIDDLEWARE_CLASSES += ('testmaker.middleware.testmaker.TestMakerMiddleware',)
        #call_command('runserver', addrport=addrport, use_reloader=False)
        import django
        from django.core.servers.basehttp import run, AdminMediaHandler, WSGIServerException
        from django.core.handlers.wsgi import WSGIHandler
        if args:
            raise CommandError('Usage is runserver %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)

        use_reloader = options.get('use_reloader', True)
        admin_media_path = options.get('admin_media_path', '')
        shutdown_message = options.get('shutdown_message', '')
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        def inner_run():
            print "Validating models..."
            self.validate(display_num_errors=True)
            print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
            print "Development server is running at http://%s:%s/" % (addr, port)
            print "Quit the server with %s." % quit_command
            try:
                path = admin_media_path or django.__path__[0] + '/contrib/admin/media'
                handler = AdminMediaHandler(WSGIHandler(), path)
                run(addr, int(port), handler)
            except WSGIServerException, e:
                # Use helpful error messages instead of ugly tracebacks.
                ERRORS = {
                    13: "You don't have permission to access that port.",
                    98: "That port is already in use.",
                    99: "That IP address can't be assigned-to.",
                }
                try:
                    error_text = ERRORS[e.args[0].args[0]]
                except (AttributeError, KeyError):
                    error_text = str(e)
                sys.stderr.write(self.style.ERROR("Error: %s" % error_text) + '\n')
                # Need to use an OS exit because sys.exit doesn't work in a thread
                os._exit(1)
            except KeyboardInterrupt:
                if create_fixtures:
                    if verbosity > 0:
                        print "Creating fixture at " + fixturefile

                    serial_file = open(fixturefile, 'w')
                    objects = []
                    for mod in get_models(get_app(app)):
                        objects.extend(mod._default_manager.all())
                    #Got models, now get their relationships.
                    #Thanks to http://www.djangosnippets.org/snippets/918/
                    related = []
                    collected = set([(x.__class__, x.pk) for x in objects])  #Just used to track already gotten models
                    for obj in objects:
                        for f in obj._meta.fields :
                            if isinstance(f, ForeignKey):
                                new = getattr(obj, f.name) # instantiate object
                                if new and not (new.__class__, new.pk) in collected:
                                    collected.add((new.__class__, new.pk))
                                    related.append(new)
                        for f in obj._meta.many_to_many:
                            if isinstance(f, ManyToManyField):
                                for new in getattr(obj, f.name).all():
                                    if new and not (new.__class__, new.pk) in collected:
                                        collected.add((new.__class__, new.pk))
                                        related.append(new)
                    if related != []:
                        objects.extend(related)
                    try:
                        serializers.serialize("json", objects, stream=serial_file)
                    except Exception, e:
                        print ("Unable to serialize database: %s" % e)
                    sys.exit(0)
        inner_run()
