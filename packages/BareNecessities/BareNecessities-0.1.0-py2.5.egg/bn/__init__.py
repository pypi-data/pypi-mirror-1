class AttributeDict(dict):
    def __getattr__(self, name):
        if not self.has_key(name):
            raise AttributeError('No such attribute %r'%name)
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        raise NotImplementedError(
            'You cannot set attributes of this object directly'
        )

