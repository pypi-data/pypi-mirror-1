# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import optparse, os, sys, mimetypes, csv

from ConfigParser import SafeConfigParser
from urlparse import urljoin

from stellaris.client import GraphClient, QueryClient, SystemClient
from stellaris.client.parsers import SPARQLResults
from stellaris.client import __VERSION__

class ConfigFileMissing(Exception): pass

class ClientConfig(object):
    def __init__(self, path):
        self.__path = os.path.abspath(os.path.expanduser(path))
        
        if not os.path.exists(self.__path):
            os.mkdir(self.__path)
        
        self.__cfg_file = os.path.join(self.__path, 'client.cfg')
        self._parse()

    @property
    def base_path(self):
        return self.__path
        
    @property
    def service_url(self):
        return self.__config['service']['service_url']
    
    @property
    def graph_prefix(self):
        return self.__config['service']['graph_prefix']

    @property
    def graph_url(self):
       return urljoin(self.service_url, self.graph_prefix)

    @property
    def default_index(self):
        return self.__config['service']['default_index']
    
    @property
    def query_prefix(self):
        return '/query/'

    @property
    def system_prefix(self):
        return '/system/'

    @property
    def key_path(self):
        return os.path.abspath(os.path.expanduser(self.__config['security']['private_key']))

    @property
    def cert_path(self):
        return os.path.abspath(os.path.expanduser(self.__config['security']['certificate']))
    
    def exists(self):
        return os.path.exists(self.__cfg_file)

    def _parse(self):
        config = SafeConfigParser()
        config.read([self.__cfg_file])
        
        data = {}
        
        for sec in config.sections():
            data[sec] = {}
            
            for (item,value) in config.items(sec):
                data[sec][item] = value

        self.__config = data
        
    def _write(self, data=None):
        """
        Writes the current config to disk or takes the given config and writes
        it to disk.
        """
        cfg = SafeConfigParser()
        
        if not data:
            data = self.__config
            
        for section in data:
            cfg.add_section(section)
            for item in data[section]:
                cfg.set(section, item, data[section][item])

        cfg.write(file(self.__cfg_file, 'w'))
        self.__config = data            

    def config_guide(self):
        if not self.exists():
            default_values = {'service_url': 'http://localhost:24000/',
                                'private_key': '',
                                'certificate': '',
                                'graph_prefix': '/',
                                'default_index': 'query'}
        else:
            default_values = {'service_url': self.service_url,
                              'graph_prefix': self.graph_prefix,
                              'private_key': self.key_path,
                              'certificate': self.cert_path,
                              'default_index': self.default_index}

        def read_data(msg, default):
            return raw_input('%s [%s]> ' % (msg, str(default))).strip() or default
            
        ret = {'service': {}, 'security': {}}
        print "StellarIS client configuration guide."
        print "-------------------------------------"
        print
        print "This guide will create a new client configuration file."
        print "If you want to change the values, then edit the file directly or"
        print "re-run this guide by giving the option --configure."
        print 
        print "Please enter the default Stellaris service you want to use."
        ret['service']['service_url'] = read_data('Service URL', default_values['service_url'])
        print
        print "A service may have defined a prefix for the name of stored graphs."
        print "If the service used by this client uses a prefix, please enter it"
        print "below."
        ret['service']['graph_prefix'] = read_data('Graph prefix', default_values['graph_prefix'])
        print
        print "A service can expose different indices to exectue queries over."
        print "Please enter the name of the default index you want to use. This"
        print "value is overridden by using the --index option when calling the client."
        ret['service']['default_index'] = read_data('Default index', default_values['default_index'])
        print
        print "X.509 certificates are used to authenticate a connecting client"
        print "In order to enable client authentication please enter the path to"
        print "your public (certificate) and private key."
        ret['security']['private_key'] = read_data('Private Key', default_values['private_key'])
        ret['security']['certificate'] = read_data('Certificate', default_values['private_key'])
        print "Saving configuration file: %s." % self.__cfg_file
        print
        try:
            self._write(data=ret)
        except Exception, e:
            sys.exit("Could not write the configuration file: %s\n" % str(e))
        print "Configuration file was written successfully written. Run the client"
        print "again with --help to get information about available commands."
        print

class ConsoleClient(object):
    
    def __init__(self, config_path):
        config_path = os.path.abspath(os.path.expanduser(config_path))
        
        cfg = ClientConfig(config_path)
        
        if not cfg.exists():
            cfg.config_guide()

        self.cfg = cfg
        
    def _init_optparser(self):
        p = optparse.OptionParser(version="Stellaris Client %s" % __VERSION__, usage="%prog [options] <command>")
        p.add_option("-s", "--service", action="store", type="string", dest="service",
                     default="http://localhost:24000", help="The service URL that the client will connect to.")
        p.add_option("", "--configure", action="store_true", dest="configure",
                     default=False, help="Run the configuration guide.")
        p.add_option("-i", "--index", action="store", dest="index",
                     default=None, help="Run the configuration guide.")
        p.add_option("", "--key", action="store", dest="key_path",
                     default='', help="Absolute path to a private key used for SSL/TLS.")
        p.add_option("", "--cert", action="store", dest="cert_path",
                     default='', help="Absolute path to a certificate used for SSL/TLS.")
        p.add_option("", "--recursive", action="store_true", dest="recursive",
                     default=False, help="Performs the operation recursively.")
        p.add_option("-o", "--output", action="store", dest="output_path",
                     default=None, help="Filename where output data is written, defaults to stdout.")
        p.add_option("", "--graph-version", action="store", dest="version",
                     default=None, help="Version of the retrieved graph.")

        return p

    def _error_msg(self, msg):
        sys.exit("[ERROR]: %s" % msg)
                    
    def execute_command(self, args):
        op = self._init_optparser()
        (opts, args) = op.parse_args(args=args)
        

        cfg = self.cfg
        
        if opts.configure:
            cfg.config_guide()
            sys.exit(1)
        
        if len(args) < 1:
            op.print_version()
            op.print_help()
            sys.exit(1)        
                   
        module = args[0]
        
        self.dispatch(module, opts, args[1:])

    def dispatch(self, module, opts, args):
        try:
            f = getattr(self, '_dispatch_%s' % module)
        except AttributeError, e:
            self._error_msg('%s is not a valid command' % module)
            
        f(opts, args)
        
    def _dump_data(self, data, path=None):
        if not path:
            f = sys.stdout
        else:
            if os.path.exists(path):
                i = 1
                path += '.%s' % str(i)
                
                while os.path.exists(path):
                    i += 1
                    path = path[:path.rfind('.')+1] + str(i)
                
            f = file(path, 'w')

        f.write(data)
        f.close()      

    def _read_data(self, path):
        if not os.path.exists(path):
            self._error_msg('Input file does not exist: %s' % path)
        return ''.join([l for l in file(path)])

    def _opt_arg(self, args, index, default=None):
        try:
            return args[index]
        except IndexError, e:
            return default

    def _opt_arg_fail(self, args, index, msg=''):
        val = self._opt_arg(args, index) 
        if val == None:
            self._error_msg(msg)
        return val
                                                
    # query <file_path> [output_path] [format]
    # query indices

    def _dispatch_query(self, opts, args):
        index = opts.index
        if index == None:
            index = self.cfg.default_index
            
        client = QueryClient(self.cfg.service_url, index_name=index, base_path=self.cfg.base_path, query_prefix=self.cfg.query_prefix)

        index_or_path = self._opt_arg_fail(args, 0, msg='"indices" nor query input file defined.')
        
        if args[0] == 'indices':
            print 'List of indexes:'
            print '----------------'
            for index in client.indices():
                print index
            return
        
        in_path = index_or_path
        output_path = opts.output_path # self._opt_arg(args, 1)
        format = opts.format # self._opt_arg(args, 2, 'xml')        
        
        data = client.query(self._read_data(args[0]), format=format)
        self._dump_data(data, path=output_path)

    # graph create <name> <file_path>
    # graph retrieve <name> [output_path] [version]
    # graph delete <name>
    # graph update <name> <file_path>
    # graph remove <name> <file_path>
    # graph replace <name> <file_path>
    # graph append <name> <file_path>
    # graph atomic_operations <name> <file_path>
    
    def _dispatch_graph(self, opts, args):
        op = self._opt_arg_fail(args, 0, 'Graph command not defined.')
        
        client = GraphClient(self.cfg.service_url, base_path=self.cfg.base_path, graphs_prefix=self.cfg.graph_prefix)
        
        graph_name = self._opt_arg_fail(args, 1, 'Graph name not defined.')
        if op == 'retrieve':
            output_path = opts.output_path
            version = opts.version
            stat, data = client.retrieve(graph_name, version=version)
            self._dump_data(data, path=output_path)
        elif op == 'delete':
            client.delete(graph_name)
        elif op == 'create':
            input_path = self._opt_arg_fail(args, 2, 'Cannot create graph without an input file.')
            mime_type, _ = mimetypes.guess_type(input_path)
            client.create(graph_name, self._read_data(input_path), mime_type)
        elif op in ['update', 'remove', 'replace', 'append']:
            f = getattr(client, 'graph_%s' % op)
            # name + file_path
            input_path = self._opt_arg_fail(args, 2, 'Cannot modify a graph without an input file.')
            mime_type, _ = mimetypes.guess_type(input_path)            
            f(graph_name, self._read_data(input_path), mime_type)
        elif op == 'atomic_operations':
            input_path = self._opt_arg_fail(args, 2, 'Cannot apply atomic operations without an input file.')
            ops = []
            try:
                reader = csv.reader(open(input_path, "rb"))
                for row in reader:
                    if row[0] in ['append', 'remove', 'update']:
                        ops.append((row[0], os.path.abspath(row[1].strip())))
                    else:
                        sys.exit('%s contains an invalid operation: %s' % (input_path, row[0]))
            except IOError, e:
                if e.errno == 2:
                    sys.exit('Could not find atomic operations input file: %s' % input_path)
            client.graph_atomic_operations(graph_name, ops)
        else:
            self._error_msg('%s is not a valid graph command.' % op)
            
    # collection add_group <collection_name> <group_name> <rights>
    # collection remove_group <collection_name> <group_name>
    # collection list <collection_name>
    # collection backup <collection_name> <output_path> [<recursive>]
    
    def _dispatch_collection(self, opts, args):
        client = SystemClient(self.cfg.service_url, base_path=self.cfg.base_path, system_prefix=self.cfg.system_prefix)
        op = self._opt_arg_fail(args, 0, 'Collection command not defined.')

        collection_name = self._opt_arg_fail(args, 1, 'Collection name not defined.')
        
        if op == 'list':
            collections, graphs = client.collection_retrieve(collection_name)
            
            print 'Sub-collections:'
            for collection in collections:
                print collection
                
            print
            print 'Graphs:'
            for graph in graphs:
                print graph
        elif op == 'add_group':
            group_name = self._opt_arg_fail(args, 2, 'Group name necessary when adding a new group.')
            rights = self._opt_arg_fail(args, 3, 'The rights for the new group is missing.')
            client.collection_add_group(collection_name, group_name, access_rights=rights)
        elif op == 'remove_group':
            group_name = self._opt_arg_fail(args, 2, 'Cannot remove group from collection without a group name.')
            client.collection_remove_group(collection_name, group_name)
        elif op == 'backup':
            output_path = self._opt_arg_fail(args, 2, 'Output file name is missing.')
            recursive = opts.recursive
            client.collection_backup(collection_name, output_path, recursive=recursive)
        else:
            self._error_msg('%s is not a valid collection command.' % op)
            
    # group list
    # group create <name>
    # group delete <name>
    # group retrieve <name>
    # group add <group_name> <user_name>
    # group remove <group_name> <user_name>
    # group replace <group_name> <file_path>

    def _dispatch_group(self, opts, args):
        client = SystemClient(self.cfg.service_url, base_path=self.cfg.base_path, system_prefix=self.cfg.system_prefix)
        op = self._opt_arg_fail(args, 0, 'Group command not defined.')

        if op == 'list':
            print "Groups:"
            for group in client.group_list():
                print group
            return

        group_name = self._opt_arg_fail(args, 1, 'Group name not defined.')                    
        if op in ['create', 'delete']:        
            f = getattr(client, 'group_%s' % op)        
            f(group_name)
        elif op == 'retrieve':
            print "Users in %s: " % group_name
            for user in client.group_retrieve(group_name):
                print user
        elif op == 'add':
            user_name = self._opt_arg_fail(args, 2, 'User name not defined.')
            users = client.group_retrieve(group_name)
            users.append(user_name)
            client.group_update(group_name, users=users)
        elif op == 'remove':
            users = client.group_retrieve(group_name)
            user_name = self._opt_arg_fail(args, 2, 'User name not defined.')            
            try:
                users.remove(user_name)
            except ValueError, e:
                self._error_msg('The given user, %s, was not in the group.' % user_name)
            client.group_update(group_name, users=users)
        elif op == 'replace':
            f = getattr(client, 'group_update')        
            f(group_name, self._read_data(args[2]).splitlines())
        else:
            self._error_msg('%s is not a valid group command.' % op)

    # index list
    # index recover <index_name>
    
    def _dispatch_index(self, opts, args):
        client = SystemClient(self.cfg.service_url, base_path=self.cfg.base_path, system_prefix=self.cfg.system_prefix)
        op = self._opt_arg_fail(args, 0, 'Index command not defined.')

        if op == 'list':
            'Available indices:'
            for index in client.indices():
                print index
        elif op == 'recover':
            index_name = self._opt_arg_fail(args, 1, 'Index name not defined.')
            client.recover_index(index_name)
        else:
            self._error_msg('%s is not a valid index command.' % op)            
                    
def run(config_path='~/.stellaris/', args=None):

    if not args:
        args = sys.argv[1:]

    c = ConsoleClient(config_path)
    c.execute_command(args)
    

#    graph_client = GraphClient(cfg.service_url, base_path=cfg.base_path, graphs_prefix=cfg.graph_prefix)
#    system_client = SystemClient(cfg.service_url, base_path=cfg.base_path, system_prefix=cfg.system_prefix)
#    query_client = QueryClient(cfg.service_url, index_name=index, base_path=cfg.base_path, query_prefix=cfg.query_prefix)
            

