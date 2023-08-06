""" repoze.obob sample application """

class Root:
    def __call__(self):
        return 'hello world!'

root = Root()

def getroot(request):
    return root

