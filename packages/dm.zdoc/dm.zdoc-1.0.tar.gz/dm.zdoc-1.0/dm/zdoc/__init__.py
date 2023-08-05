import App.FindHomes # activate Zope's import magic

# rebind 'pydoc.locate' to prevent reloading -- as this deactivates Zope's import magic
from pydoc import *
import pydoc

org_locate = locate
def locate(path, *args, **kw):
 if args: args = (False,) + args[1:]
 if 'forceload' in kw: kw['forceload'] = False
 return org_locate(path, *args, **kw)

pydoc.locate = locate

if __name__ == '__main__': cli()
                              
