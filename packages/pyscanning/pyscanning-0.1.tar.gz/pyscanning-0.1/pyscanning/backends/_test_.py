from wrapper import BaseScanner, BaseScannerCollection
import Image
import os

class ScannerCollection(BaseScannerCollection):
    def __init__(self):
        self.__devices__ = []
 
    def __refresh__(self):
        self.__devices__ = []
        scanner = Scanner(0, "Pyscan", "Test Device")
        self.__devices__.append(scanner)
    
    def get(self, scanner_id):
        self.__refresh__()
        id = int(scanner_id)
        for dev in self.__devices__:
            if dev.id == id:
                return dev
        return None

    def list(self):
        self.__refresh__()
        return tuple([scanner.info() for scanner in self.__devices__])

class Scanner(BaseScanner):  
    def __init__(self, id, manufacturer, name):
        self.id = id
        self.manufacturer = manufacturer
        self.name = name

    def __str__(self):
        return '%s- %s: %s' % (self.id, self.manufacturer, self.name)
    
    def scan(self):
        imgpath = os.path.dirname(__file__)+"/../testdata/img1.tiff"
        return Image.open(imgpath)
    
    def info(self):
        return {'id': self.id, 
                'manufacturer': self.manufacturer, 
                'name': self.name}
   
    def __close__(self):
        pass
