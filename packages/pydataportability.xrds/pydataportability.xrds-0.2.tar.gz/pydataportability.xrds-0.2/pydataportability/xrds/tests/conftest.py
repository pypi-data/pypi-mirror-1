import os

def pytest_funcarg__fp1(request):
    filename = os.path.abspath(os.path.dirname(__file__))+"/example1.xrds"
    fp = open(filename)
    return fp


def pytest_funcarg__fp2(request):
    filename = os.path.abspath(os.path.dirname(__file__))+"/example2.xrds"
    fp = open(filename)
    return fp
    
