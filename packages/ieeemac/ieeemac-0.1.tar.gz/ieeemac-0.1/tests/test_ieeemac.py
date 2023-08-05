from nose.tools import *
from ieeemac import Mac, ismac, main

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

def bad_case(m):
    assert ismac(m) == False
