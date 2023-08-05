#!/Library/Frameworks/Python.framework/Versions/2.4/Resources/Python.app/Contents/MacOS/Python

from TileCache import Service, cgiHandler, cfgfiles

if __name__ == '__main__':
    svc = Service.load(*cfgfiles)
    cgiHandler(svc)

