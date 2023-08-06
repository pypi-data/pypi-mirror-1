from wrapper import BaseScanner, BaseScannerCollection
import sane

class ScannerCollection(BaseScannerCollection):
    def __init__(self):
        self.__devices__ = []
 
    def __refresh__(self):
        for scanner in self.__devices__:
            scanner.__close__()
        self.__devices__ = []
        sane.exit()


        sane.init()
        devices = sane.get_devices()    
        for dev in devices: 
            id = len(self.__devices__)
            try:
                scanner = Scanner(id, dev[0], dev[1], dev[2], dev[3])
                self.__devices__.append(scanner)
            except:
                pass
    
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
    def __init__(self, id, device, manufacturer, name, description):
        self.id = id
        self.manufacturer = manufacturer
        self.name = name
        self.description = description
        self.__scanner__ = sane.open(device)

    def __str__(self):
        return '%s- %s: %s' % (self.id, self.manufacturer, self.name)
    
     
    
    def scan(self):
        return self.__scanner__.scan()
    
    def info(self):
        return {'id': self.id, 
                'manufacturer': self.manufacturer, 
                'name': self.name, 
                'description': self.description}
   
    def __close__(self):
        self.__scanner__.close()
    # TODO:     
    #def status(self):
    #    pass
