# it is important that the environmnet module gets imported as the
# very first module in each handler.
import environment
import tornado.web
import tornado.wsgi
import tornado.template
import wsgiref.handlers
import os

# initialize the loader for tornado templates
templates = tornado.template.Loader('templates')

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        tmpl = templates.load("index.html")
        self.write(tmpl.generate(
            title="lovely.gae example project",
            content="This is the lovely.gae example project"))

app  = tornado.wsgi.WSGIApplication([
    (r"/", MainHandler),
    ])

def main():
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == "__main__":
    main()

