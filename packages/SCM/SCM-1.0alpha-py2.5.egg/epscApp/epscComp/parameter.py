
class Parameters(object):
    """ parameters for optimization
    """
    def __init__(self,name='',active=0,value=[],comment=''):
        self.name = name
        self.active = active
        self.value = value
        self.comment = comment

    def setValue(self,value):
        self.value = value

    def setActive(self,active):
        self.active = active

    def setComment(self,comment):
        self.comment = comment


if __name__ == '__main__':
    pass