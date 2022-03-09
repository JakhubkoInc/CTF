

class property_value_to_be(object):

    def __init__(self, locator, property_name, property_value):
        self.locator = locator
        self.property_name = property_name
        self.property_value = property_value
    
    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        return element.get_attribute(self.property_name) == self.property_value

class can_find(object):

    def __init__(self, locator):
        self.locator = locator
    
    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            return True
        except:
            return False

class can_find_any(object):

    def __init__(self, locator):
        self.locator = locator
    
    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        return len(elements) > 0
            
class property_value_to_contain(object):

    def __init__(self, locator, property_name, property_value):
        self.locator = locator
        self.property_name = property_name
        self.property_value = property_value
    
    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            return str(element.get_attribute(self.property_name)).__contains__(self.property_value)
        except:
            print(f"expectedConditions: property_value_to_contain: cannot find {self.locator}, returning false")
            return False

class lambda_condition(object):

    def __init__(self, locator, condition):
        self.locator = locator
        self.condition = condition
    
    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        return self.condition(element)