from Products.Five.browser import BrowserView

class RSS2View(BrowserView):

    def __call__(self, *args, **kw):
        r = ['<content:encoded>']
        r.append('<h1>hello world</h1>')
        r.append('</content:encoded>')
        return '\n'.join(r)

