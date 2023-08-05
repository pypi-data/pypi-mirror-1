"""Pudge Command Line Interface Tests"""

import getopt

import pudge.cli as cli
from pudge.generator import Generator

def test_bad_arguments():
    command = cli.PudgeCommand('pudge', ['-XX'])
    try:
        command.parse_arguments()
    except getopt.GetoptError, e:
        pass # good!
    else:
        assert 0, ("PudgeCommand.parse_arguments() should have raised an "
                  "exception.")

def test_usage():
    command = cli.PudgeCommand('pudge', ['-h'])
    call = command.parse_arguments()
    assert not isinstance(call, Generator)

def test_short_args():
    args = ['-f', '-x',
            '-d', '/test/dest',
            '-t', '/test/templates',
            '-m', 'pudge']
    command = cli.PudgeCommand('pudge', args)
    call = command.parse_arguments()
    assert isinstance(call, Generator)
    assert call.force
    assert call.xhtml
    assert call.dest == '/test/dest'
    assert call.template_dir == '/test/templates'
    assert call.modules == ['pudge']

def test_long_args():
    args = ['--force', '--xhtml',
            '--dest=/test/dest',
            '--templates=/test/templates',
            '--modules=pudge']
    command = cli.PudgeCommand('pudge', args)
    call = command.parse_arguments()
    assert isinstance(call, Generator)
    assert call.force
    assert call.xhtml
    assert call.dest == '/test/dest'
    assert call.template_dir == '/test/templates'
    assert call.modules == ['pudge']
    
