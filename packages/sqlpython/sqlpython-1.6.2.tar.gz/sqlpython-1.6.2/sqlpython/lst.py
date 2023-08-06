class L(list):
    def __new__(cls, a, b, *args):
        instance = list.__new__(cls, args)
        instance.a = a
        instance.b = b
        return instance