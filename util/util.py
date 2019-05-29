""" Util library """
import re

def is_overlapped(_x0: tuple, _x1: tuple):
    """ Overlapping lines on x axis """
    return bool(set(range(_x0[0], _x0[1]+1)) & set(range(_x1[0], _x1[1]+1)))


class Version:
    """ Semantic Versioning comparing library
        reference: https://semver.org/

        Supports fix and minor versions up to 999
    """

    def __init__(self, value: str):
        pattern = re.compile(r'^(\d+)\.(\d+)(\.(\d+))*$')
        self.major, self.minor, _, self.fix = pattern.match(value).groups()

    def __gt__(self, other):
        return self.__int__() > other.__int__()

    def __ge__(self, other):
        return self.__int__() >= other.__int__()

    def __eq__(self, other):
        return self.__int__() == other.__int__()

    def __int__(self):
        fix = self.fix or 0
        return (int(self.major) * 1000000 +
                int(self.minor) * 1000 + int(fix))

    def __str__(self):
        if self.fix:
            return '{}.{}.{}'.format(self.major, self.minor, self.fix)
        return '{}.{}'.format(self.major, self.minor)
