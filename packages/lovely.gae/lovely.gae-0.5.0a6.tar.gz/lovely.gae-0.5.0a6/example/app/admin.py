# it is important that the environmnet module gets imported as the
# very first module in each handler.
import environment
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import lovely.gae.async
import lovely.gae.snapshot


# create an application with all lovely.gae entry points
app = webapp.WSGIApplication(
    lovely.gae.async.HANDLER_TUPLES + \
    lovely.gae.snapshot.HANDLER_TUPLES,
    debug=True)

def main():
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()
