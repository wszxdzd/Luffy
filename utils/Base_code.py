
class Base_statue_code(object):
    def __init__(self):
        self.code = 1000
        self.error = ""
        self.data = ""

    @property
    def dict(self):
        return self.__dict__
