import os

is_test = os.getenv('PYSCANNING_TEST')
if is_test and is_test.lower() == 'true':
    from backends._test_ import ScannerCollection
elif os.name == 'posix':
    from backends._sane_ import ScannerCollection
elif os.name == 'nt':
    from backends._twain_ import ScannerCollection
else:
    #TODO: Log error
    raise Exception('OS not supported')

__scanners__ = ScannerCollection()
del ScannerCollection


def list():
    return __scanners__.list()

def get(id):
    return __scanners__.get(id)
