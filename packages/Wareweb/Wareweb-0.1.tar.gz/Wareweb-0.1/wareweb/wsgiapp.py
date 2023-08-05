import os
from paste.util import import_string, findpackage
from paste import urlparser
from paste.deploy.converters import asbool
from paste.deploy.config import ConfigMiddleware

def make_wareweb_app(
    global_conf,
    servlet_directory=None,
    package_name=None,
    complete_stack=True,
    debug=False,
    # session middleware:
    cookie_name='_SID_',
    session_file_path='/tmp',
    # error middleware:
    error_email=None,
    error_log=None,
    show_exceptions_in_wsgi_errors=False,
    from_address=None,
    smtp_server=None,
    error_subject_prefix=None,
    error_message=None,
    # enabling:
    profile=False,
    profile_limit=40,
    **app_conf):
    if package_name:
        package = package_name
        if isinstance(package, (str, unicode)):
            package = import_string.simple_import(package)
        package_dir = os.path.dirname(package.__file__)
    else:
        package = None
        package_dir = '' # @@: ?
    if servlet_directory:
        if package_dir:
            servlet_directory = os.path.join(package_dir, servlet_directory)
    else:
        servlet_directory = os.path.join(package_dir, 'web')

    url_package_name = findpackage.find_package(servlet_directory)
    app = urlparser.URLParser(
        global_conf, servlet_directory, url_package_name)

    combined_conf = global_conf.copy()
    combined_conf.update(app_conf)
    app = ConfigMiddleware(app, combined_conf)

    if asbool(complete_stack):
        from paste import session, recursive, httpexceptions
        from paste.exceptions import errormiddleware
        app = recursive.RecursiveMiddleware(
            app, global_conf)
        app = session.SessionMiddleware(
            app, global_conf, cookie_name=cookie_name,
            session_file_path=session_file_path)
        app = httpexceptions.middleware(
            app, global_conf)
        app = errormiddleware.ErrorMiddleware(
            app, global_conf,
            debug=debug,
            error_email=error_email,
            show_exceptions_in_wsgi_errors=show_exceptions_in_wsgi_errors,
            from_address=from_address,
            smtp_server=smtp_server,
            error_subject_prefix=error_subject_prefix,
            error_message=error_message,
            )
        
        if asbool(debug):
            from paste import printdebug
            app = printdebug.PrintDebugMiddleware(
                app, global_conf)

    if asbool(profile):
        from paste import profilemiddleware
        app = profilemiddleware.ProfileMiddleware(
            app, global_conf, limit=int(profile_limit))
    
    return app

            
