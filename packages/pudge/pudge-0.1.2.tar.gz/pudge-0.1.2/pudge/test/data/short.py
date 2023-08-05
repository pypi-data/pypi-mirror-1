"""Short scanner test file."""
# be very careful modifying this file because the tests are sensitive to line
# numbers

#:6-9
attribute = 10

#:9-13
def function(arg1, arg2, kw1=None):
    pass

#:13-21
class OldClass:
    #:15-16
    attribute = 20
    #:17-19
    def method(self, arg1, arg2, kw1=None):
        pass

#:21-27
class NewClass(object):
    #:23-24
    attribute = 30
    #:25-27
    def method(self, arg1, arg2, kw1=None):
        pass

#:28
