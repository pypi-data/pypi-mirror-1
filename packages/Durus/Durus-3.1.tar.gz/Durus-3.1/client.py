#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/durus/client.py $
$Id: client.py 26303 2005-03-08 14:08:46Z dbinger $
"""
import sys
import os
from code import InteractiveConsole
from durus.utils import p64, u64
from durus.file_storage import FileStorage
from durus.client_storage import ClientStorage
from durus.connection import Connection
from durus.storage_server import DEFAULT_PORT, DEFAULT_HOST, wait_for_server
from pprint import pprint

def configure_readline(namespace, history_path):
    try:
        import readline, rlcompleter, atexit
        readline.set_completer(
            rlcompleter.Completer(namespace=namespace).complete)
        readline.parse_and_bind("tab: complete")
        def save_history(history_path=history_path):
            readline.write_history_file(history_path)
        atexit.register(save_history)
        if os.path.exists(history_path):
            readline.read_history_file(history_path)
    except ImportError:
        pass

def interactive_client(file, host, port, cache_size, readonly, repair,
                       startup):
    if file:
        storage = FileStorage(file, readonly=readonly, repair=repair)
        description = file
    else:
        wait_for_server(host, port)
        storage = ClientStorage(host=host, port=port)
        description = "%s:%s" % (host, port)
    connection = Connection(storage, cache_size=cache_size)
    namespace = {'connection': connection,
                 'root': connection.get(0),
                 'get': connection.get,
                 'sys': sys,
                 'os': os,
                 'p64': p64,
                 'u64': u64,
                 'pp': pprint}
    configure_readline(namespace, os.path.expanduser("~/.durushistory"))
    console = InteractiveConsole(namespace)
    if startup:
        console.runsource('execfile("%s")' % os.path.expanduser(startup))
    help = ('    connection -> the connection\n'
            '    root       -> get(0)\n'
            '    get(oid)   -> get an object\n'
            '    pp(object) -> pretty-print')
    console.interact('Durus (%s)\n%s' % (description, help))

def client_main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.set_description("Opens a client connection to a Durus server.")
    parser.add_option(
        '--file', dest="file", default=None,
        help="If this is not given, the storage is through a Durus server.")
    parser.add_option(
        '--port', dest="port", default=DEFAULT_PORT,
        type="int",
        help="Port the server is on. (default=%s)" % DEFAULT_PORT)
    parser.add_option(
        '--host', dest="host", default=DEFAULT_HOST,
        help="Host of the server. (default=%s)" % DEFAULT_HOST)
    parser.add_option(
        '--cache_size', dest="cache_size", default=10000,
        type="int",
        help="Host of the server. (default=0, no limit)")
    parser.add_option(
        '--repair', dest='repair', action='store_true',
        help=('Repair the filestorage by truncating to remove anything '
              'that is malformed.  Without this option, errors '
              'will cause the program to report and terminate without '
              'attempting any repair.'))
    parser.add_option(
        '--readonly', dest='readonly', action='store_true',
        help='Open the file in read-only mode.')
    parser.add_option(
        '--startup', dest='startup',
        default=os.environ.get('DURUSSTARTUP', ''),
        help=('Full path to a python startup file to execute on startup.'
              '(default=DURUSSTARTUP from environment, if set)')
        )
    (options, args) = parser.parse_args()
    interactive_client(options.file, options.host, options.port,
                       options.cache_size, options.readonly, options.repair,
                       options.startup)


if __name__ == '__main__':
    client_main()
