class BaseScannerCollection(object):

    def __init__(self):
        raise NotImplementedError

    def getScanner(self):
        raise NotImplementedError

    def list(self):
        return self

class BaseScanner(object):

    def __init__(self):
        raise NotImplementedError

    def scan(self):
        raise NotImplementedError

    def info(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError

