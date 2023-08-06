from nose.tools import *
from ieeemac import Mac, ismac, main, find_macs

def test_valid():
    ok = [
        ('00:11:22:33:44:55', 'unix',    '00:11:22:33:44:55'),
        ('00:11:22:33:44:55', 'cisco',   '0011.2233.4455'),
        ('00:11:22:33:44:55', 'windows', '00-11-22-33-44-55'),
        ('00:11:22:33:44:55', 'bare',    '001122334455'),

        ('0:11:22:33:44:55',  'cisco',   '0011.2233.4455'),
        ('0:1:2:3:4:5',       'cisco',   '0001.0203.0405'),
        ('001122334455',      'cisco',   '0011.2233.4455'),
        ('0011.2233.4455',    'unix',    '00:11:22:33:44:55'),
        ]
    for input, fmt, output in ok:
        yield ok_case, input, fmt, output

def ok_case(input, fmt, output):
    m = Mac(input)
    out = m.to_format(fmt)
    print 'checking', out, output
    assert out == output
    assert ismac(input)


def test_invalid():
    bad = [
        '00:11:22-33-44-55',

        '00:11:22:33:44:5g',
        '00112233445g',

        '0:1:2:3:4:g',
        '00:11:22::44:55',
        '111.111.111',
        ]
    for b in bad:
        yield bad_case, b

    yield bad_case, ''
    yield bad_case, None

def bad_case(m):
    assert ismac(m) == False


def test_formats():
    m = Mac('00:11:22:33:44:55')
    f = m.formats
    assert len(f)==4

def test_to_attributes():
    m = Mac('00:11:22:33:44:55')
    assert m.to_unix == '00:11:22:33:44:55'
    assert m.to_windows == '00-11-22-33-44-55'
    assert m.to_cisco == '0011.2233.4455'
    assert m.to_bare == '001122334455'

    try:
        xxx = m.xxx
        assert False
    except AttributeError:
        return

def test_str():
    a1 = '00:01:02:03:04:05'
    a2 = '00:1:2:3:4:5'
    m = Mac(a1)
    assert str(m) == a1

    m = Mac(a2)
    assert str(m) == a1

def test_eq():
    a1 = '00:01:02:03:04:05'
    a2 = '00:1:2:3:4:5'

    assert a1      != a2
    assert Mac(a1) == Mac(a2)
    assert Mac(a1) == a2

    assert Mac(a1) != a1.replace('5','a')
    assert Mac(a1) != Mac(a1.replace('5','a'))

def test_find_macs():
    inputs = [
        "hello there 00:11:22:33:44:55 mac",
        "hello mac=00:11:22:33:44:55, ip=",
    #this finds ac:00:11:22:33:44
    #   "hello mac:00:11:22:33:44:55, ip",
    ]

    for input in inputs:
        yield find_case, input, ['00:11:22:33:44:55']

def find_case(input, expected):
    out = find_macs(input)
    print out
    assert out == expected
