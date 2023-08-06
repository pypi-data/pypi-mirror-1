d9t.json
========

  >>> from d9t.json import parser

Let's define some json data.

  >>> json = """ {'data1':null, 'data2':'something', 'data3':[1,2,3,'string',true,{'datanested':'something','floatdata':44.22, 'bool':false}]} """
  >>> domparser = parser.JsDomParser(json)
  >>> data = domparser.parse()
  >>> data
  {'data1': None, 'data3': [1, 2, 3, 'string', True, {'datanested': 'something', 'bool': False, 'floatdata': 44.219999999999999}], 'data2': 'something'}

That's it ;)

