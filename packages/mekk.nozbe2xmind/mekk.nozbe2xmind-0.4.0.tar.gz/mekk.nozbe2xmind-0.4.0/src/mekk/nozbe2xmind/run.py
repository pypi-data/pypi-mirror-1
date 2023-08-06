# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

import os

usage = """
Generating XMind mind-map with your Nozbe projects and tasks:

    %prog download --map=file.xmind --user=<your nozbe username>

Listing changes you made on this mind-map (what-happened):

    %prog info --map=file.xmind

Uploading changes made on the mind-map (don't do it twice or
you will add the same actions twice!):

    %prog upload --map=file.xmind --user=<your nozbe username>

"""

def parse_options():
    from optparse import OptionParser
    opt_parser = OptionParser(
                              usage=usage)
    opt_parser.add_option("-u", "--user",
                          action="store", type="string", dest="user",
                          help ="Your Nozbe username")
    opt_parser.add_option("-m", "--map",
                          action="store", type="string", dest="map",
                          help="The name of the output XMind file")
    opt_parser.add_option("-c", "--completed",
                          action="store_true", dest = "completed",
                          help = "Include completed tasks (not downloaded by default)")
    opt_parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose",
                          help="Print diagnostic messages")
    opt_parser.add_option("-d", "--devel",
                          action="store", type="string", dest="devel",
                          help="Use development installation. Give --devel=user,pwd (http auth for devel site)")
    opt_parser.set_defaults(verbose = False, completed = False)
    (opts, args) = opt_parser.parse_args()

    if not len(args) == 1:
        opt_parser.error("Operation not selected (download, info, or upload)")
    operation = args[0]
    if not operation in ['download', 'info', 'upload']:
        opt_parser.error("Invalid operation: %s. Expected: download, info, or upload" % operation)

    if (operation in ['download', 'upload']) and not opts.user:
        opt_parser.error("This operation requires --user=<your-nozbe-username>")
    if (operation in ['info', 'upload']):
        if not opts.map:
            opt_parser.error("This operation requires --map=your-xmind-file")
        if not os.path.isfile(opts.map):
            opt_parser.error("File %s does not exist" % opts.map)
    if operation == 'download':
        if not opts.map:
            opt_parser.error("This operation requires --map=<created-xmind-file>")

    if opts.devel:
        import re
        m = re.match("^([^,]+),([^,]+)$", opts.devel)
        if not m:
            opt_parser.error("Bad syntax for devel option (expected user,pwd)")
        opts.devel = dict(user = m.group(1), password = m.group(2))
    return operation, opts

operation, options = parse_options()

from mekk.nozbe2xmind import nozbe_to_xmind
from mekk.nozbe import NozbeApi, CachingNozbeApi, NozbeKeyringConnection
from mekk.nozbe2xmind.run_analysis import upload_changes, print_changes_info
from twisted.internet import reactor, defer
import logging
logging.basicConfig(level = (options.verbose and logging.DEBUG or logging.WARN))

@defer.inlineCallbacks
def main():
    try:
        if operation in ['download', 'upload']:
            connection = NozbeKeyringConnection(options.user, options.devel)
            yield connection.obtain_api_key()

        if operation == "download":
            api = CachingNozbeApi(connection)
            yield nozbe_to_xmind(api, options.map, options.devel, options.completed)
            print "XMind map saved to %s" % options.map
        elif operation == "info":
            print_changes_info(options.map)
        elif operation == "upload":
            api = NozbeApi(connection)
            yield upload_changes(api, options.map)
        else:
            raise Exception("Unknown operation")
    except Exception, e:
        if options.verbose:
            raise
        else:
            print "Failure: ", e
    finally:
        reactor.stop()

def run():
    reactor.callLater(0, main)
    reactor.run()

if __name__ == "__main__":
    run()
