#IGNORE FOR NOW

#In order to use Anobind to serialize back to XML, you must mix-in
#Code that interprets Bird as an element

class Bird:
    def __init__(self, name, wingspan):
        self.name = name
        self.wingspan = wingspan

b = Bird("Golden Eagle", "230cm")

