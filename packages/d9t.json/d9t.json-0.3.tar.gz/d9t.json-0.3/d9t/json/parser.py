import re

STRING="string"
FLOAT="float"
INT="int"
CONTROL="control"
KEYWORD="keyword"

class JsParse(object):
    """
        Parses a json-like string
        Example:
        '{"name":"from: somewhere to: somewhereelse@41.839421,3.309283","Status":{"code":200,"request":"directions"},"Placemark":[{"id":...'
        This lib makes no result, it just calls callback methods.
        Intergers and floats are recognized.

        Usage
        =====
        >>> j = JsParse(result)
        >>> j.parse()

        You may want to derive from JsParse and overwrite the callback-methods
        which are called c_* and are called on the appropriate events.
    """

    _string_start = ('"',"'")
    _quote = "\\"
    _list_start = "["
    _list_end = "]"
    _dict_start = "{"
    _dict_end = "}"
    _splitter = ","
    _key_value_splitter = ":"

    def __init__(self, res):
        self.res = res

    def parse_string(self, index=0):
        # this parses a string and returns it and the new index (after the string ends)
        _string_end = self.res[index]
        if _string_end not in self._string_start:
            raise "String does not start here."

        index += 1
        start = index

        while True:
            # find next _string_end
            end = self.res.find(_string_end, index)
            if self.res[end-1] != self._quote:
                return (end+1, self.res[start:end], STRING)
            index = end+1

    def parse_number(self, index=0):
        _str = []
        for i in xrange(index, len(self.res)):
            if self.res[i]=="." or self.res[i].isdigit():
                _str.append(self.res[i])
            else:
                value = "".join(_str)
                if "." in value:
                    return (i, float(value), FLOAT)
                return (i, int(value), INT)

        # finally, if the number is the end of self.res
        value = "".join(_str)
        if "." in value:
            return (len(self.res), float(value), FLOAT)
        return (len(self.res), int(value), INT)

    def parse_keyword(self, index=0):
        match = re.match('[a-zA-Z0-9_]+', self.res[index:])
        if not match:
            # TODO: raise?
            return
        keyword = match.group()
        return (len(keyword)+index, keyword, KEYWORD)

    def parse(self, index=0):
        reslen = len(self.res)
        while index < reslen:
            (index, result, result_type) = self.next(index)
            if result is not None:
                if result_type==STRING:
                    self.c_string(result)
                elif result_type==FLOAT:
                    self.c_float(result)
                elif result_type==INT:
                    self.c_int(result)
                elif result_type==KEYWORD:
                    self.c_keyword(result)
                elif result_type==CONTROL:
                    if result == "[":
                        self.c_list_start()
                    elif result == "]":
                        self.c_list_end()
                    elif result == "{":
                        self.c_dict_start()
                    elif result == "}":
                        self.c_dict_end()
                    elif result == ",":
                        self.c_splitter()
                    elif result == ":":
                        self.c_key_value_splitter()
                #yield result

    def next(self, index):
        c = self.res[index]
        if c in self._string_start:
            return self.parse_string(index)
        if c.isdigit():
            return self.parse_number(index)
        if c == self._list_start:
            return (index+1, "[", CONTROL)
        if c == self._dict_start:
            return (index+1, "{", CONTROL)
        if c == self._list_end:
            return (index+1, "]", CONTROL)
        if c == self._dict_end:
            return (index+1, "}", CONTROL)
        if c == self._splitter:
            return (index+1, ",", CONTROL)
        if c == self._key_value_splitter:
            return (index+1, ":", CONTROL)
        if c in (" ", "\t"):
            return (index+1, None, None)
        # is it a keyword?
        if c.isalnum():
            return self.parse_keyword(index)
        raise "Invalid char %s on index %d" % (repr(c), index)

    # callback functions
    def c_string(self, value):
        print "String: %s" % value

    def c_float(self, value):
        print "Float: %f" % value

    def c_int(self, value):
        print "Int: %d" % value

    def c_dict_start(self):
        print "Starting dict"

    def c_dict_end(self):
        print "Ending dict"

    def c_list_start(self):
        print "Starting list"

    def c_list_end(self):
        print "Ending list"

    def c_splitter(self):
        print "Splitter"

    def c_key_value_splitter(self):
        print "Key/Value Splitter"

    def c_keyword(self, value):
        print "Keyword: %s" % value



class JsDomParser(JsParse):
    """
        Implements a dict access on the received values.

        Usage
        =====
        >>> d = JsDomParser(result)
        >>> data = d.parse()
    """


    _in_dict_key = 0
    _dict_key = None

    def __init__(self, res):
        self.res = res
        self._stack = []

    @property
    def depth(self):
        return len(self._stack)-1

    @property
    def current(self):
        try:
            return self._stack[-1]
        except IndexError:
            return None

    def append(self, what):
        # if we are in a dict, use the current dict
        # key to create a new what on the stack and
        # reference to it.
        # If we are in a list, just append a new
        # what and reference to it.
        # If we are in neither, just set the what
        # and reference to it.
        if type(self.current) is dict:
            # we should have a dict_key.
            self.current[self._dict_key] = what
            self._stack.append(self.current[self._dict_key])
        elif type(self.current) is list:
            self.current.append(what)
            self._stack.append(self.current[-1])
        else:
            # initialize
            self._stack.append(what)
            self._stack.append(what)

    def c_string(self, value):
        if type(value) is str:
            #value = value.decode("iso-8859-1")
            pass
        if self._in_dict_key:
            self._dict_key = value
        elif type(self.current) is dict:
            self.current[self._dict_key] = value
        elif type(self.current) is list:
            self.current.append(value)
        else:
            self._stack.append(value)

    c_float = c_int = c_string

    def c_keyword(self, value):
        table = {
                'null': None,
                'true': True,
                'false': False,
                }
        self.c_string(table.get(value, None)) # TODO: better raise instead of return None?

    def c_dict_start(self):
        self._in_dict_key = True
        self.append(dict())

    def c_dict_end(self):
        self._stack.pop()

    def c_list_start(self):
        self.append(list())

    def c_list_end(self):
        self._stack.pop()

    def c_splitter(self):
        # if list, all is done by c_string.
        # if dict, switch mode
        if type(self.current) is dict:
            self._in_dict_key = True

    def c_key_value_splitter(self):
        self._in_dict_key = False

    def parse(self):
        super(JsDomParser, self).parse()
        return self._stack[0]

