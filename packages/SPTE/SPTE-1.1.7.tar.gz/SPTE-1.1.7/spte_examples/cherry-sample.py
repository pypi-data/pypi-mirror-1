import cherrypy
import spte

expose = cherrypy.expose

class Controller:
    @expose
    @spte.template(file='html.spte')
    def index(self):
        lista = ['uno', 'dos', 'tres', 'cuatro', 'cinco']
        lista2 = [lista[-i] for i in range(1, len(lista)+1)]
        return dict(titulo='Mi ejemplo',
                lista=lista,
                lista2=lista2,
                subtemplate='example.spte')

cherrypy.quickstart(Controller())

