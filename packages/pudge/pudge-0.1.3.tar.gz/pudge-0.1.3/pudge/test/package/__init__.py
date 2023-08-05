"""A cool blurb about the package.

You can use `Restructured Text`_ in your doc strings. This let's us do such
cool things as...

* bullet
* ed
* lists

as well as..

1. number 
2. ed
3. lists

oh, and definition lists..

true statment
  the following statement is false.
false statement
  the preceding statement is true.

and code blocks like this::

  # to say hi, use the print statement:
  print 'hi.'

and blockquotes too:

  Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean
  vulputate augue et magna. Nunc id nibh. Vestibulum sit amet wisi at
  nisl elementum nonummy. Sed faucibus, ipsum in gravida rhoncus, diam
  orci vulputate justo, non laoreet massa turpis quis enim. Nullam
  iaculis, dolor ut dignissim tristique, sapien diam tristique leo, sed
  adipiscing dui velit et ipsum. Pellentesque egestas pede quis
  orci. Curabitur consequat vulputate quam. Integer vel dui. Curabitur
  eget purus sit amet tellus semper viverra. Etiam vestibulum vulputate
  sem.

not to mention footnotes [1]_, *emphasis*, **strong**, ``teletype``, and
`cite` inline styles.

.. _restructured text: http://docutils.sourceforge.net/rst.html
.. [1] this a footnote about an uninteresting topic.

"""

# this will show up if no __all__ is defined because we don't know
# where it came from.
from math import pi


def func(x, y, z=pi):
    """A cool blurb about ``func``.
    
    Aenean sit amet elit. Proin elit. Pellentesque accumsan augue ac
    wisi. Mauris ligula dui, fermentum eu, consectetuer ut, mollis at,
    pede. Donec sit amet tellus bibendum arcu ultrices mattis. Proin arcu
    metus, porta sit amet, ultricies eget, venenatis in, diam. Phasellus
    iaculis, sapien vitae lobortis vehicula, mi felis scelerisque orci, eu
    pretium quam neque a nibh. Aenean ut elit. Praesent adipiscing
    vestibulum nulla. Mauris volutpat est commodo wisi. Cras
    fermentum. Aenean elementum posuere dolor.Quisque nec elit. Etiam massa
    wisi, imperdiet ac, accumsan et, porttitor ut, massa. Aliquam erat
    volutpat. Mauris pede justo, tincidunt quis, sagittis et, sollicitudin
    eu, urna. Sed nonummy pede eget enim. Pellentesque eget nunc. Vestibulum
    ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia
    Curae; Pellentesque non nisl.
    """
    return (x * y) ** z

class Class:
    """A cool blurb about this class.
    
    Pellentesque semper aliquam orci. In nec massa tempor lectus laoreet
    fermentum. Ut dignissim mauris id sapien. Sed quis urna quis quam
    facilisis hendrerit. In consectetuer turpis sed mauris. Fusce
    adipiscing. Cras nibh velit, tempor vitae, laoreet vel, sollicitudin
    id, dolor. Proin adipiscing metus quis neque. Fusce elementum congue
    erat. Suspendisse eu tellus.
    """

    def __init__(self, foo):
        """Construct an instance of Class"""
        pass

    def before(self):
        """Methods are sorted by name.."""
    
    def method(self, x, y, z=1):
        """A cool blurb about this method.

        Etiam ullamcorper commodo sapien. Maecenas a lacus. Sed
        convallis dui sit amet enim. Etiam lacinia. Nulla et
        velit. Vestibulum iaculis ante. Vestibulum venenatis sem
        malesuada metus. Etiam in mi. Duis venenatis quam ut odio. Nulla
        euismod nunc at ligula. Pellentesque nulla diam, convallis in,
        sodales eu, mattis at, nibh. Nulla at erat. In hac habitasse
        platea dictumst. Phasellus vehicula tellus sit amet dui. Duis
        tortor. Proin nibh nisl, egestas eget, mattis ac, dictum sit
        amet, felis. Pellentesque laoreet, turpis sit amet mollis
        fringilla, enim eros dapibus ligula, quis tempus urna elit et
        tellus. Curabitur ullamcorper interdum risus. Donec dictum
        tellus et ante.
        
        """
        pass
    
    # documentation on this attribute.
    name = 5678

# documentation on this attribute
name = 1234

# this should be excluded from Module.all()
import string
