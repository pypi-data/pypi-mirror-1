#!/Library/Frameworks/Python.framework/Versions/2.5/Resources/Python.app/Contents/MacOS/Python
import pexpect
import sys
import time
import os
import optparse
from suxsync.ssh_session import ssh_session

defaults={}
defaults['username']=os.environ['USER']
defaults['password']=""

parser = optparse.OptionParser()

parser.add_option("-u", "--username", dest="username", metavar="USERNAME", default=defaults['username'],
                  help="What username do we connect as?")

parser.add_option("-o", "--hostname", dest="hostname", metavar="HOSTNAME", 
                  help="To which server are we connecting?")
                  
parser.add_option("-p", "--password", dest="password", metavar="PASSWORD", default=defaults['password'],
                  help="SSH Password")                  

parser.add_option("-c", "--command", dest="command", metavar="COMMAND", 
                  help="The command you wish to remotely execute.")  
    
(options, args) = parser.parse_args()

try:
    assert options.hostname
    assert options.command
    assert options.username
except AssertionError, ae:
    parser.print_help()
    parser.error("You must at least provide a username, hostname and a command.")


command = "ssh %s@%s %s" % (options.username, options.hostname,options.command)
conn = pexpect.spawn( command, timeout=1500 )
conn.expect('.*ssword:')
conn.sendline('%s' % options.password )
conn.read()

