from tgwebservices.controllers import WebServicesRoot, WebServicesController, \
                                      wsexpose, wsvalidate

from tgwebservices.runtime import typedproperty, unsigned

class MyService(WebServicesRoot):
    @wsexpose(int)
    @wsvalidate(int)
    def times2(self, value):
        "Multiplies value by two."
        return value * 2
    
    @wsexpose(int)
    @wsvalidate(int)
    def twentyover(self, value):
        "Divides 20 by value"
        return 20 / value
    
class FancyValue(object):
    name = ""
    age = int
    
    def computed(self):
        return "Hello!"
    computed = typedproperty(str, computed)
    
    def __init__(self, name=None, age=None):
        self.name = name
        self.age = age

class ComplexProperty(object):
    def athing(self):
        return FancyValue("Arnie", 55)
    athing = typedproperty(FancyValue, athing)

class ReadWriteProperty(object):
    def setvalue(self, value):
        self._value = value
    def getvalue(self):
        return self._value
    value = typedproperty(str, getvalue, setvalue)

class FoodItem(object):
    person = FancyValue
    quantity = unsigned
    
    def __init__(self, name=None, quantity=1):
        self.person = FancyValue(name)
        self.quantity = quantity

class SubFood(FoodItem):
    price = 1.95

class FoodOrder(object):
    name = ""
    items = [FoodItem]

class ComplexService(WebServicesRoot):
    
    @wsexpose(FancyValue)
    def getfancy(self):
        "Returns a fancy value"
        fv = FancyValue()
        fv.name = "Mr. Test"
        fv.age = 33
        return fv
    
    @wsexpose(SubFood)
    def getsub(self):
        sf = SubFood()
        return sf
    
    @wsexpose([FancyValue])
    def getmulti(self):
        return [FancyValue("Mr. Washington", 274), 
                FancyValue("Mr. Lincoln", 197)]
    
    @wsexpose([FancyValue])
    def getempty(self):
        return []
    
    @wsexpose([str])
    def somestrings(self):
        return ["A", "B", "C"]
    
    @wsexpose(FoodOrder)
    def getorder(self):
        order = FoodOrder()
        order.name = "WHC"
        order.items = [FoodItem("Burger"), FoodItem("Fries", 2)]
        return order
    
    @wsexpose(ComplexProperty)
    def getcomprop(self):
        return ComplexProperty()
    
    @wsexpose(FancyValue)
    @wsvalidate(FancyValue)
    def tenyearsolder(self, person):
        person.age = person.age + 10
        self.last_person = person
        return person

    @wsexpose(ReadWriteProperty)
    @wsvalidate(ReadWriteProperty)
    def getandsetrwprop(self, rwp):
        r = ReadWriteProperty()
        r.value = rwp.value
        return r

class InnerService(WebServicesController):
    def __init__(self, add_another=False):
        if add_another:
            self.foo = InnerService()
        
    @wsexpose(FancyValue)
    def getFancy(self):
        return FancyValue("Mr. Bean", 42)

class OuterService(WebServicesRoot):
    inner = InnerService(True)
    another = InnerService()

    @wsexpose(int)
    def ultimatequestion(self):
        return 42
