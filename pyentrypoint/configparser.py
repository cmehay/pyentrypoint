from configparser import ConfigParser as CP
from io import StringIO


class ConfigParser(CP):
    '''
    ConfigParser class with to_string method to convert config to string
    and write it inside jinja template and read methods which return
    self object
    '''

    def to_string(self):
        io = StringIO()
        self.write(io)
        return io.getvalue()

    def read(self, *args, **kwards):
        super().read(*args, **kwards)
        return self

    def read_dict(self, *args, **kwards):
        super().read_dict(*args, **kwards)
        return self

    def read_file(self, *args, **kwards):
        super().read_file(*args, **kwards)
        return self

    def read_string(self, *args, **kwards):
        super().read_string(*args, **kwards)
        return self

    def __str__(self):
        return self.to_string()
