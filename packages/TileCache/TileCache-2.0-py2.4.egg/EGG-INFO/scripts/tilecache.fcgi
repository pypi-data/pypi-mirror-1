#!/Library/Frameworks/Python.framework/Versions/2.4/Resources/Python.app/Contents/MacOS/Python
from TileCache.Service import wsgiApp

if __name__ == '__main__':
    from flup.server.fcgi_fork  import WSGIServer
    WSGIServer(wsgiApp).run()
