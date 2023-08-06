import os
import sys
import subprocess
import xmlrpclib
import optparse


class BotController(object):

    def __init__(self, host, port):
        self.host = host
        self.port = str(port)

    @property
    def server_url(self):
        return 'http://%s:%s' % (self.host, self.port)

    def rpc_command(self, cmdname, *args):
        server = xmlrpclib.Server(self.server_url)
        command = getattr(server, cmdname)
        try:
            command(*args)
        except xmlrpclib.Fault, e:
            print >> sys.stderr, 'Error: %s' % e.faultString.split(':', 1)[1]

    def say(self, network, channel, s):
        spaces = ''
        lines = [x.rstrip() for x in s.split('\n') if x.strip()]
        for line in lines:
            self.rpc_command('privmsg', network, channel, spaces+line)
            spaces = '  '


class Revision(object):

    def __init__(self, repo, rev):
        self.repo = repo
        self.rev = rev

        self.commit_msg = self._svnlook('log')
        self.author = self._svnlook('author')
        self.reponame = self.repo.split(os.path.sep)[-1]
        self.num_modified = len(self._svnlook('changed').split('\n'))

    def _svnlook(self, cmd):
        cmdargs = ['svnlook', cmd, self.repo, '-r', self.rev]
        output = subprocess.Popen(cmdargs,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).communicate()[0]
        return output.strip()


class SVNBlabber(object):

    COMMIT_MSG = 'SVN [%(reponame)s] %(author)s r%(rev)s : ' \
        '%(num_modified)i modified : ' \
        '%(extra)s%(msg)s\n  %(url)s'

    def __init__(self, repo, network, channel,
                 bothost='localhost', botport=7766,
                 rev_url=None):
        self.repo = repo
        self.botcontroller = BotController(bothost, botport)
        self.network = network
        self.channel = channel
        self.rev_url = rev_url

    def report_commit(self, revnum):
        rev = Revision(self.repo, revnum)

        if rev.commit_msg.find('\n') > -1:
            extra = '\n'
        else:
            extra = ''

        if self.rev_url:
            url = self.rev_url % {'repo': rev.reponame, 'rev': rev.rev}
        else:
            url = ''
        msg = self.COMMIT_MSG % {'author': rev.author, 'rev': rev.rev,
                                 'extra': extra,
                                 'num_modified': rev.num_modified,
                                 'reponame': rev.reponame,
                                 'msg': rev.commit_msg,
                                 'url': url}

        self.botcontroller.say(self.network, self.channel, msg)


USAGE = """%prog <network> <channel> <repopath> <rev>

  <network>    IRC network to use (ie freenode)
  <channel>    IRC channel to post to
  <repopath>   Path to SVN repository
  <rev>        SVN revision to get info about"""


def main(argv=sys.argv[1:]):
    parser = optparse.OptionParser(usage=USAGE)
    parser.add_option('-a', '--address', action='store', dest='address',
                      help='IP address of IRC bot')
    parser.add_option('-p', '--port', action='store', dest='port',
                      type='int', help='Port of IRC bot')
    parser.add_option('-r', '--rev_url', action='store', dest='rev_url',
                      help='Revision URL to use (ie looks like '
                           'http://somehost.com/%(repo)s/%(rev)s)')

    (opts, args) = parser.parse_args(argv)

    if len(args) == 0:
        parser.print_help()
        return

    network, channel, repo, revnum = args

    kwargs = {}
    if opts.address:
        kwargs['bothost'] = opts.address
    if opts.port:
        kwargs['botport'] = opts.port
    if opts.rev_url:
        kwargs['rev_url'] = opts.rev_url
    blabber = SVNBlabber(repo, network, channel, **kwargs)
    blabber.report_commit(revnum)

if __name__ == '__main__':
    main()
