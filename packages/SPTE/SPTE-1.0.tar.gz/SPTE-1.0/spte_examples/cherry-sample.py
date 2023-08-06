import cherrypy
import spte

expose = cherrypy.expose

class template:
    def __init__(self, file='template.spte'):
        self.file = file
    def __call__(self, f):
        def templated(*args):
            vars = f(*args)
            return spte.render(self.file, vars)
        return templated

class Controller:
    @expose
    @template(file='html.spte')
    def index(self):
        lista = ['uno', 'dos', 'tres', 'cuatro', 'cinco']
        lista2 = [lista[-i] for i in range(1, len(lista)+1)]
        return dict(titulo='Mi ejemplo',
                lista=lista,
                lista2=lista2,
                subtemplate='example.spte')

cherrypy.quickstart(Controller())

