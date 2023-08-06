from optparse import make_option

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run a Paster Server."
    option_list = BaseCommand.option_list + (
        make_option('--port', dest='port', default=8080, type='int',
                    help='Makes the server bind to this port.'),
        make_option('--host', dest='host', default='127.0.0.1',
                    help='Makes the server bind to this host.'),
    )
    args = "[port, host]"

    def handle(self, *args, **options):
        from paste import httpserver
        from paste import fileapp
        from paste import urlmap
        import django.core.handlers.wsgi
        from django.conf import settings
        from django.utils import translation
        from django.core.servers.basehttp import AdminMediaHandler

        print "Validating models..."
        self.validate(display_num_errors=True)

        # Activate the current language.
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass

        # Run WSGI handler for the application
        project_app = django.core.handlers.wsgi.WSGIHandler()

        # Hookup the admin files.
        path = django.__path__[0] + '/contrib/admin/media'
        full_app = AdminMediaHandler(project_app, path)

        # Setup the media folder.
        static_app = fileapp.DirectoryApp(settings.MEDIA_ROOT)
        mapping = urlmap.URLMap(not_found_app=full_app)
        mapping[settings.MEDIA_URL] = static_app

        print 'Starting...'
        httpserver.serve(mapping, port=options['port'], host=options['host'])


    def usage(self, subcommand):
        return "help"
