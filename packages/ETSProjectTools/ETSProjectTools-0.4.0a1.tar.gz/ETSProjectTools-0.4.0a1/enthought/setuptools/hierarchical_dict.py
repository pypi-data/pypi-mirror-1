
SEPARATOR = "/"

class HierarchicalDict(dict):
    """ A dictionary that can optionally create a hierarchy of nested
    dictionaries in response to insertion with a key that can be 
    interpreted to be a series of keys.
    """

    # Whether or not to create hierarchical nested dictionaries
    nested = True

    # When using nested, the token separating elements
    delimiter = SEPARATOR

    def __init__(self, nested=True, delimiter=SEPARATOR, *args, **kw):
        super(HierarchicalDict, self).__init__(*args, **kw)
        self.nested = nested
        self.delimiter = delimiter

    def __getitem__(self, key):
        if not self.nested:
            return dict.__getitem__(self, key)
        else:
            elements = key.split(self.delimiter)
            item = dict.__getitem__(self, elements[0])
            if len(elements) > 1:
                return item[self.delimiter.join(elements[1:])]
            else:
                return item

    def __setitem__(self, key, val):
        if not self.nested:
            return dict.__setitem__(self, key, val)
        else:
            elements = key.split(self.delimiter)
            cur_key = elements[0]

            if len(elements) == 1:
                dict.__setitem__(self, cur_key, val)
            else:
                if cur_key not in self:
                    subdict = HierarchicalDict()
                    subdict.nested = self.nested
                    subdict.delimiter = self.delimiter
                    dict.__setitem__(self, cur_key, subdict)
                else:
                    subdict = dict.__getitem__(self, cur_key)
                subdict[self.delimiter.join(elements[1:])] = val
        return

    def __lines__(self):
        """ Returns this dict's contents as a series of lines, without
        opening or closing braces
        """
        lines = []
        template = "'%r': %r"
        indent = "   "
        for i, (key, val) in enumerate(self.items()):
            if not isinstance(val, dict):
                lines.append("%r: %r" % (key, val))
            else:
                lines.append("%r: {" % key)
                lines.extend([indent+x for x in val.__lines__()])
                lines.append(indent + "}")
            if i != len(self) - 1:
                lines[-1] += ","
        return lines


    def __str__(self):
        lines = self.__lines__()
        return "{" + "\n".join([" "+x for x in lines])[1:] + "\n}"


