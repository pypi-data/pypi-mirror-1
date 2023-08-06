import commands, os, sys, socket, logging
from time import sleep

def setup_module(module):
    # Reformat db
    base_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir))
    outs = commands.getstatusoutput('rm %s/test_project/test.db' % base_path)
    outs = commands.getstatusoutput('cd %s/test_project ; python manage.py syncdb' % base_path)
    assert not outs[0]
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        stream=sys.stdout
                        )
    
    sys.path.append(base_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'

    import django.core.handlers.wsgi
    _application = django.core.handlers.wsgi.WSGIHandler()

    def application(environ, start_response):
        environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
        return _application(environ, start_response)
        
    import cherrypy
    httpd = cherrypy.wsgiserver.CherryPyWSGIServer(('0.0.0.0', 7887), application, server_name='windmill-http')
    from threading import Thread
    httpd_thread = Thread(target=httpd.start)
    httpd_thread.setDaemon(True)
    httpd_thread.start()
    sleep(.5)
        
    module.httpd_thread = httpd_thread
    module.httpd = httpd
    
def teardown_module(module):
    module.httpd.stop()
    while module.httpd_thread.isAlive():
        sleep(.5)