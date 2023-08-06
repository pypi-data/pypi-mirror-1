from Products.Five.browser import BrowserView

class Dissect(BrowserView):
    def __call__(self):
        
        page = ""
        metodos = dir(self.context)
	# removing the __roles__ methods
	metodos = [m for m in metodos if not '__roles__' in m.lower() and not m.startswith('manage_') ]
        
        page += '<h1> There are %d available methods/attributes in <strong> %s </strong> </h1> ' % (len(metodos), self.context.absolute_url())
        page += '<table border="1px">'
        page += '<tr><th>%s</th><th>%s</th></tr>' % ("Methods", "Value")
        for m in metodos:
            try:
                valor = self.context.restrictedTraverse(m)
                if callable(valor) and m != 'unindexObject':
                    valor = valor()
                page += '<tr><td><strong>%s<strong></td><td>%s</td></tr>' % (m, valor)
            except:
              pass
        page += '</table>'

        return page

