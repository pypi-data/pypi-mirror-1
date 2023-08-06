import os

def pytest_funcarg__xrd1fp(request):
    filename = os.path.abspath(os.path.dirname(__file__))+"/basic1.xrd"
    fp = open(filename)
    return fp
    
    