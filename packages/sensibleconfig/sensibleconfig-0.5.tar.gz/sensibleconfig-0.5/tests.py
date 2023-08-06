
import os, tempfile

from sensibleconfig import Config, Option

options = [
    Option('opt1', 'opt1-help', 'od', 'o'),
    Option('int1', 'int1-help', 1, 'i', int),
    Option('long1', 'long1-help', 'lo'),
]

def test_basic():
    conf = Config(options, 'TEST')
    assert conf.opt1 == 'od'

def test_long_argv():
    conf = Config(options, 'TEST')
    conf.grab_from_argv(['--opt1', 'do'])
    assert conf.opt1 == 'do'

def test_short_opt():
    conf = Config(options, 'TEST')
    conf.grab_from_argv(['-o', 'do'])
    assert conf.opt1 == 'do'

def test_env():
    conf = Config(options, 'TEST')
    os.environ['TEST_OPT1'] = 'do'
    conf.grab_from_env()
    assert conf.opt1 == 'do'

def test_convert_default():
    conf = Config(options, 'TEST')
    assert conf.int1 == 1

def test_convert_argv():
    conf = Config(options, 'TEST')
    conf.grab_from_argv(['--int1', '2'])
    assert conf.int1 == 2

def test_convert_env():
    conf = Config(options, 'TEST')
    os.environ['TEST_INT1'] = '2'
    conf.grab_from_env()
    assert conf.int1 == 2

def test_empty_shortname():
    conf = Config(options, 'TEST')
    assert conf.long1 == 'lo'
    conf.grab_from_argv(['-l', 'ol'])
    assert conf.long1 == 'ol'

def _create_temp_config_file():
    fd, fn = tempfile.mkstemp()
    os.write(fd, '[config]\nopt1=fo\nint1=7\n')
    os.close(fd)
    return fn

def test_file():
    fn = _create_temp_config_file()
    conf = Config(options, 'TEST')
    conf.grab_from_file(fn)
    assert conf.opt1 == 'fo'
    os.unlink(fn)

def test_convert_file():
    fn = _create_temp_config_file()
    conf = Config(options, 'TEST')
    conf.grab_from_file(fn)
    assert conf.int1 == 7
    os.unlink(fn)

def test_from_dict():
    conf = Config(options, 'TEST')

    d = {
        'opt1': 'banana',
        'int1': 999,
    }

    assert conf.opt1 == 'od'
    assert conf.int1 == 1

    conf.grab_from_dict(d)

    assert conf.opt1 == 'banana'
    assert conf.int1 == 999


def test_to_dict():
    conf = Config(options, 'TEST')


    assert conf.to_dict() == {
        'opt1': 'od',
        'long1': 'lo',
        'int1': 1,
    }

def test_remainder_argv():
    conf = Config(options, 'TEST')
    posit = conf.grab_from_argv(['--opt1', 'do', 'moo'])
    assert conf.opt1 == 'do'
    assert posit == ['moo']


