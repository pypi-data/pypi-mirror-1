import paste.deploy
from sqlalchemy import clear_mapper, create_engine, create_session
from sqlalchemy.ext.assignmapper import assign_mapper
from sqlalchemy.ext.sessioncontext import SessionContext
import pylons.database
import quickwiki.models as model

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup quickwiki here.
    """
    conf = paste.deploy.appconfig('config:' + filename)
    paste.deploy.CONFIG.push_process_config({'app_conf':conf.local_conf,
                                             'global_conf':conf.global_conf})

    uri = conf['sqlalchemy.dburi']
    engine = create_engine(uri)
    print "Connecting to database %s" % uri
    model.meta.connect(engine)
    print "Creating tables"
    model.meta.create_all()

    # Pylons' session_context expects the g and request objects to be setup
    # (within a request). This is a Pylons 0.9.4 bug. A workaround is to
    # create a new assign_mapper with a SessionContext that works outside of
    # requests.
    clear_mapper(model.page_mapper)
    assign_mapper(SessionContext(lambda: create_session(bind_to=engine)),
                  model.Page, model.pages_table)

    print "Adding front page data"
    page = model.Page()
    page.title = 'FrontPage'
    page.content = 'Welcome to the QuickWiki front page.'
    page.flush()
    print "Successfully setup."

