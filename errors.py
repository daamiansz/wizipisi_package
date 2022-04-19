class FileNameException:
    class FileNameNotInPackage(Exception):
        def __init__(self, filename):
            self.filename=filename
        def __str__(self):
            return self.filename+" nie znajduje się w paczce"
            
    class ObjectNotExist(Exception):
        def __init__(self, object_name):
            self.object_name=object_name
        def __str__(self):
            return self.object_name+" nie istnieje"
