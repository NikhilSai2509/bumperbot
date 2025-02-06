# class Example:
#     def __init__(self, value):
#         self.value = value  # Instance variable

#     def set_value(self, value):
#         value = value  # This is a local variable
#         self.value = value  # This sets the instance variable

#     def display(self):
#         print(f"Instance variable value: {self.value}")

# # Using Example class
# example = Example(70)
# example.set_value(90)
# example.display()  # Output: Instance variable value: 90

class Person:
    def __init__(self, name, age):
        # Instance variable
        self.name = name
        self._age = age  # Protected variable

    # Property to get age
    @property
    def age(self):
        return self._age

    # Property to set age with validation
    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("Age cannot be negative!")
        self._age = value

# Usage
p = Person("Alice", 25)
print(p.age)  # Access age via property: 25
p.age = 30    # Update age with validation
print(p.age)  # Output: 30

 # Raises ValueError
