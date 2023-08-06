d9t.json
========

  >>> from d9t.json import parser

Let's define some json data.

  >>> json = """ {'data1':null, 'data2':'something', 'data3':[-1.42,2,-3,.34,-.55',string',true,{'datanested':'something','floatdata':44.22, 'bool':false}]} """
  >>> domparser = parser.JsDomParser(json)
  >>> data = domparser.parse()

  >>> sorted(data.keys())
  ['data1', 'data2', 'data3']

  >>> data["data1"] is None
  True

  >>> data["data2"]
  'something'

  >>> len(data['data3'])
  8

  >>> data['data3'][0] == -1.42
  True

  >>> data['data3'][1] == 2
  True

  >>> data['data3'][2] == -3
  True

  >>> data['data3'][3] == .34
  True

  >>> data['data3'][4] == -0.55
  True

  >>> data['data3'][5] == ',string'
  True

  >>> data['data3'][6] == True
  True

  >>> sorted(data['data3'][7].keys())
  ['bool', 'datanested', 'floatdata']

  >>> data['data3'][7]['bool'] == False
  True

  >>> data['data3'][7]['floatdata'] == 44.22
  True

  >>> data['data3'][7]['datanested'] == 'something'
  True




That's it ;)

