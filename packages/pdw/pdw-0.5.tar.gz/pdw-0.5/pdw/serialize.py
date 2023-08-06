import os
import simplejson

from sqlalchemy import orm


def get_table(model_class):
    table = orm.class_mapper(model_class).mapped_table
    return table


class SQLAlchemy(object):

    def to_dict(self, obj):
        '''
        obj: sqlalchemy object
        '''
        table = get_table(obj.__class__)
        return self.record_to_dict(obj, table)

    def record_to_dict(self, record, table):
        '''
        record: sqlalchemy record object for this table.
        table: sqlalchemy table.
        '''
        out = {}
        for key in table.c.keys():
            # TODO: use type information
            val  = getattr(record, key)
            out[key] = val
        return out

    def get_type(self, column):
        if hasattr(column.type, 'impl'):
            # derived types e.g. UuidType
            return column.type.impl
        else:
            return column.type

    def from_dict(self, _dict, model_class):
        # TODO: support for retrieving object based on primary keys

        table = get_table(model_class)
        # Need pk cols in order they were defined on the table
        # so that query.get works correctly
        # Hope this will do it without any further intervention
        primary_keys = [ x.name for x in table.c if x.primary_key ]
        assert len(primary_keys) > 0
        # if one in all should be in ...
        if primary_keys[0] in _dict: # existing object
            pkvals = [ _dict[k] for k in primary_keys ]
            # get takes tuple of pk vals in order of defn in table
            ourobj = model_class.query.get(*pkvals)
        else: # new object
            ourobj = model_class()
        for k,v in _dict.items():
            col = table.c[k]
            value_type = self.get_type(col)
            # TODO: convert based on value_type
            newval = v
            setattr(ourobj, k, newval)
        return ourobj


import pdw
class Dumper(object):
    '''Dump and load databases to json.

    The dumper is table oriented rather than object oriented in that it will
    dump the table corresponding to the object rather than a representation of
    the object based on its mapper. 

    A dump (and a load) can be to a single file or can be spread across a whole
    set of files (in order to cope with large databases).
    '''

    def __init__(self, model_classes, verbose=False, items_per_file=5000):
        '''
        @param model_classes: sqlalchemy model classes corresponding to items we wish
        to dump and load.
        '''
        self.model_classes = model_classes
        self.verbose = verbose
        self.items_per_file = items_per_file
    
    def _dump_multi(self, data, dir, class_count, model_class_name, item_count):
        fn = '%03d_%s_%06d.js' % (class_count, model_class_name, item_count)
        fp = os.path.join(dir, fn)
        fo = open(fp, 'w')
        simplejson.dump(data, fo, indent=4)
        fo.close()

    def _fileobj_or_dir(self, fileobj_or_dir):
        if not isinstance(fileobj_or_dir, basestring):
            fileobj = fileobj_or_dir
            dir = None
        else:
            fileobj = None
            dir = fileobj_or_dir
        return (fileobj, dir)

    def dump(self, fileobj_or_dir):
        '''Dump in JSON format to fileobj or a directory.
        
        If passed a string assume that it is a directory.
        '''
        fileobj, dir = self._fileobj_or_dir(fileobj_or_dir)
        multifile = dir is not None
        if multifile and not os.path.exists(dir):
            os.makedirs(dir)
        serializer = SQLAlchemy()
        dump_struct = { '__version__' : pdw.__version__ }
        if self.verbose:
            print "\nStarting...........................\n\n"

        class_count = 0
        for model_class in  self.model_classes:
            class_count += 1
            table = get_table(model_class)
            model_class_name = model_class.__name__
            dump_struct[model_class_name] = []
            if self.verbose:
                print model_class_name, '--------------------------------'
            q = table.select()
            count = 0
            filename_count = 0
            for record in q.execute():
                count += 1
                recorddict = serializer.record_to_dict(record, table)
                dump_struct[model_class_name].append(recorddict)
                if multifile and count % self.items_per_file == 0:
                    if self.verbose:
                        print filename_count
                    self._dump_multi(dump_struct, dir, class_count,
                            model_class_name, filename_count)
                    dump_struct = { model_class_name : [] }
                    filename_count += 1
            if multifile and not count % self.items_per_file == 0:
                self._dump_multi(dump_struct, dir, class_count,
                        model_class_name, filename_count)
                dump_struct = { model_class_name : [] }
        if not multifile:
            # Do NOT sort keys as order or serialization may be important
            simplejson.dump(dump_struct, fileobj, indent=4)

    def load(self, fileobj_or_dir):
        fileobj, dir = self._fileobj_or_dir(fileobj_or_dir)
        # Protect against writing into created database.
        for model_class in self.model_classes:
            if model_class.query.count():
                raise Exception, "Existing '%s' records in database" % model_class.__name__

        if fileobj is not None:
            self._load(fileobj)
        elif dir is not None:
            fns = sorted(os.listdir(dir))
            for fn in fns:
                if self.verbose:
                    print fn
                fp = os.path.join(dir, fn)
                fo = open(fp)
                self._load(fo)
                fo.close()
        else:
            raise ValueError('Nothing to load')

    def _load(self, fileobj):
        # force to unicode (in simplejson 2.0 not done automatically)
        data = unicode(fileobj.read(), encoding='utf8')
        dump_struct = simplejson.loads(data)
        # TODO: version checking
        # if dump_struct['__version__'] != pdw.__version__:
        #    raise Exception('You are loading a dump created with an old version')
        for model_class in self.model_classes:
            table = get_table(model_class)
            model_class_name = model_class.__name__
            count = 0
            for record_dict in dump_struct.get(model_class_name, []):
                count += 1
                if self.verbose and count % self.items_per_file == 0:
                    print '%s: %s' % (model_class_name, count)
                    print 'Current item', record_dict
                q = table.insert(values=record_dict)
                result = q.execute()
        # Create generic function to correct sequences ...
        # self.fix_sequences()
        if self.verbose:
            print 'OK'

