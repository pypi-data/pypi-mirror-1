===========	
Color Field
===========

The string contained in the field describes a RGB color in hexdecimal
format. Let's first generate a color field:

  >>> from zw.schema.color import Color
  >>> color = Color()
    
Make sure the colors validate:

  >>> color.validate('aa00cc')
  >>> color.validate('00aa000')
  Traceback (most recent call last):
  ...
  InvalidColor: 00aa000


