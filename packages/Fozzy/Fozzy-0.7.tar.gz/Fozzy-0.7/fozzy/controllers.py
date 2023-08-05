import cherrypy
from fozzy.model import *
from json import write as jsonify
from restresource import RESTResource
import turbogears
from turbogears import controllers

def build_controllers():
    cherrypy.root = Fozzy()
    cherrypy.root.application = ApplicationController()

class Fozzy:
    @cherrypy.expose
    def index(self):
        """ list applications """
        return jsonify([a.name for a in Application.select()])

class DocumentController(RESTResource):
    REST_map = {'PUT' : 'index_document'}
    def REST_instantiate(self,key,**kwargs):
        try:
            application = self.parents[0]
            return Document.select(AND(Document.q.applicationID == application.id,
                                       Document.q.key == key.encode('utf8')))[0]
        except:
            return None

    def REST_create(self,key,**kwargs):
        application = self.parents[0]
        return Document(application=application,key=key.encode('utf8'))

    def index_document(self, document, text=u""):
        document.update(text)
        return "ok"
    index_document.expose_resource = True

    def delete(self,document):
        document.destroySelf()
        return "ok"
    delete.expose_resource = True

    def index(self,document):
        return document.body
    index.expose_resource = True

class ApplicationController(RESTResource,controllers.Root):

    REST_map = {'GET' : 'search'}
    REST_children =  {'document' : DocumentController()}

    def REST_instantiate(self,name,**kwargs):
        try:
            return Application.byName(name.encode('utf8'))
        except:
            return None

    def REST_create(self,name,**kwargs):
        return Application(name=name)

    def search(self, application, q=u""):
        return jsonify(application.search(q))
    search.expose_resource = True

    def delete(self,application):
        application.destroySelf()
        return "ok"
    delete.expose_resource = True

    def add(self,application):
        return "ok"
    add.expose_resource = True

    update = add




