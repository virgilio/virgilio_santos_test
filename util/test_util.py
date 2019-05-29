""" Testing util library """

from .util import is_overlapped, Version as version


def test_simple_overlap():
    """ Simple overlap """
    assert is_overlapped((1, 5), (2, 6)) is True


def test_starting_from_root():
    """ Starting from 0 """
    assert is_overlapped((0, 3), (2, 6)) is True


def test_line_is_a_dot():
    """ The dot case """
    assert is_overlapped((1, 5), (6, 6)) is False


def test_line_contains_other():
    """ l2 contains l1 """
    assert is_overlapped((2, 5), (1, 6)) is True
    assert is_overlapped((1, 10), (6, 8)) is True


def test_invalid_line():
    """ l2 is invalid a line """
    assert is_overlapped((0, 5), (6, 2)) is False


def test_only_boundary_intersects():
    """ only the boundary intersection """
    assert is_overlapped((1, 5), (5, 6)) is True

def test_version_gt():
    """ Test if version is greater the other  """
    assert version('1.1.1') > version('1.1')
    assert version('2.0') > version('1.999.999')
    assert version('1.1') < version('1.1.1')

def test_version_ge():
    """ Test if version is greater the other """
    assert version('1.1') >= version('1.1')
    assert version('1.1.1') >= version('1.1')
    assert version('2.1') >= version('1.999.999')
    assert version('1.1') <= version('1.1')

def test_version_eq():
    """ Test if version is greater the other """
    assert version('1.1') == version('1.1')
    assert version('1.1.1') != version('2.1')

def test_version_int():
    """ Test if version 'polinomial' integer conversion """
    assert int(version('1.1')) == 1001000
    assert int(version('1.100.1')) == 1100001
    assert int(version('2.1')) == 2001000
    assert int(version('22.11')) == 22011000

def test_version_str():
    """ Test if version string method  """
    assert str(version('1.1')) == '1.1'
    assert str(version('1.100.1')) == '1.100.1'
    assert str(version('2.1')) == '2.1'
    assert str(version('22.11')) == '22.11'
