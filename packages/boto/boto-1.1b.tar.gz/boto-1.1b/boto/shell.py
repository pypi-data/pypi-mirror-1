#!/usr/bin/env python
import cmd, sys
from boto.mashups.server import Server

class ServerShell(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.servers = []
        self.current_server = None
        self.prompt = '> '

    def do_quit(self, arg):
        sys.exit(1)

    def help_quit(self):
        print 'syntax: quit',
        print '-- terminates the application'

    def do_inventory(self, args):
        self.servers = Server.Inventory()

    def help_inventory(self):
        print 'inventory (inv) - get an inventory of all your current EC2 servers'

    do_inv = do_inventory
    help_inv = help_inventory

    def do_list_servers(self, args):
        print 'ID#\tAMI_ID\tHOSTNAME'
        for i in range(0, len(self.servers)):
            s = self.servers[i]
            print '[%d]\t%s\t%s' % (i, s.ami, s.hostname)

    do_ls = do_list_servers

    def do_set_current_server(self, args):
        try:
            if args.strip() == 'all':
                self.current_server = 'all'
            else:
                index = int(args.strip())
                self.current_server = self.servers[index]
        except:
            print 'Invalid index: %s' % args

    def help_set_current_server(self):
        print 'set_current_server (scs) - Set the current working server'
        print 'SYNOPSIS'
        print 'set_current_server (scs) N|all'
        print '\tN is the index number of a server in your inventory'
        print '\t  or "all" to specify all servers in the inventory are current'

    do_scs = do_set_current_server
    help_scs = help_set_current_server

    def do_get_current_server(self, args):
        if self.current_server:
            print '%s\t%s' % (self.current_server.ami,
                              self.current_server.hostname)
        else:
            print 'No current working server'

    do_gcs = do_get_current_server

if __name__ == "__main__":
    cli = ServerShell()
    cli.cmdloop('Boto Server Shell')
    
