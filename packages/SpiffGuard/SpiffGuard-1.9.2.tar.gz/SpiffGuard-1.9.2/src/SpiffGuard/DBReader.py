# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import sys
import os.path
import datetime
from functions    import bin_path2list, list2bin_path, bin_path2hex_path
from Acl          import Acl
from Action       import Action
from Resource     import Resource
from ResourcePath import ResourcePath
import sqlalchemy                 as sa
import sqlalchemy.databases.mysql as mysql

class DBReader(object):
    """
    The main interface for accessing the database.
    """
    attrib_type_int, attrib_type_bool, attrib_type_string = range(3)

    def __init__(self, db):
        """
        Instantiates a new DBReader.
        
        @type  db: object
        @param db: An sqlalchemy database connection.
        @rtype:  DB
        @return: The new instance.
        """
        self.db            = db
        self.db_metadata   = sa.MetaData(self.db)
        self._table_prefix = 'guard_'
        self._table_map    = {}
        self._types        = {}   # Maps typename to type
        self._action_cache = {}   # Maps "handle/typename" to Action
        self._sql_cache    = {}   # Maps SQL to result
        self.__update_table_names()


    def __add_table(self, table):
        """
        Adds a new table to the internal table list.
        
        @type  table: Table
        @param table: An sqlalchemy table.
        """
        pfx = self._table_prefix
        self._table_map[table.name[len(pfx):]] = table


    def __update_table_names(self):
        """
        Adds all tables to the internal table list.
        """
        pfx = self._table_prefix
        self.__add_table(sa.Table(pfx + 'action', self.db_metadata,
            sa.Column('id',             sa.Integer,     primary_key = True),
            sa.Column('action_type',    sa.String(50),  index = True),
            sa.Column('handle',         sa.String(230), index = True),
            sa.Column('name',           sa.String(230), unique = True),
            mysql_engine='INNODB'
        ))
        self.__add_table(sa.Table(pfx + 'resource', self.db_metadata,
            sa.Column('id',            sa.Integer,     primary_key = True),
            sa.Column('resource_type', sa.String(50),  index = True),
            sa.Column('handle',        sa.String(230), index = True),
            sa.Column('name',          sa.String(230)),
            sa.Column('n_children',    sa.Integer,     index = True, default = 0),
            sa.Column('is_group',      sa.Boolean,     index = True),
            mysql_engine='INNODB'
        ))
        self.__add_table(sa.Table(pfx + 'resource_attribute', self.db_metadata,
            sa.Column('id',             sa.Integer,     primary_key = True),
            sa.Column('resource_id',    sa.Integer,     index = True),
            sa.Column('name',           sa.String(50),  index = True),
            sa.Column('type',           sa.Integer),
            sa.Column('attr_string',    sa.TEXT),
            sa.Column('attr_int',       sa.Integer),
            sa.ForeignKeyConstraint(['resource_id'],
                                    [pfx + 'resource.id'],
                                    ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(sa.Table(pfx + 'resource_path', self.db_metadata,
            sa.Column('id',             sa.Integer,     primary_key = True),
            sa.Column('path',           mysql.MSVarBinary(255), index = True),
            sa.Column('depth',          sa.Integer,     index = True),
            sa.Column('resource_id',    sa.Integer,     index = True),
            sa.ForeignKeyConstraint(['resource_id'],
                                    [pfx + 'resource.id'],
                                    ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(sa.Table(pfx + 'path_ancestor_map', self.db_metadata,
            sa.Column('resource_path_id',  sa.Integer, index = True),
            sa.Column('ancestor_path_id',  sa.Integer, index = True),
            sa.ForeignKeyConstraint(['resource_path_id'],
                                    [pfx + 'resource_path.id'],
                                    ondelete = 'CASCADE'),
            sa.ForeignKeyConstraint(['ancestor_path_id'],
                                    [pfx + 'resource_path.id'],
                                    ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))
        self.__add_table(sa.Table(pfx + 'acl', self.db_metadata,
            sa.Column('id',             sa.Integer, primary_key = True),
            sa.Column('actor_id',       sa.Integer, index = True),
            sa.Column('action_id',      sa.Integer, index = True),
            sa.Column('resource_id',    sa.Integer, index = True),
            sa.Column('permit',         sa.Boolean, index = True),
            sa.Column('last_change',    sa.DateTime, default = sa.func.now()),
            sa.ForeignKeyConstraint(['actor_id'],
                                    [pfx + 'resource.id'],
                                    ondelete = 'CASCADE'),
            sa.ForeignKeyConstraint(['action_id'],
                                    [pfx + 'action.id'],
                                    ondelete = 'CASCADE'),
            sa.ForeignKeyConstraint(['resource_id'],
                                    [pfx + 'resource.id'],
                                    ondelete = 'CASCADE'),
            mysql_engine='INNODB'
        ))


    def debug(self, debug = True):
        """
        Enable/disable debugging.

        @type  debug: Boolean
        @param debug: True to enable debugging.
        """
        if debug:
            self.db.echo = 1
        else:
            self.db.echo = 0


    def set_table_prefix(self, prefix):
        """
        Define a string that is prefixed to all table names in the database.
        Default is 'guard_'.

        @type  prefix: string
        @param prefix: The new prefix.
        """
        self._table_prefix = prefix
        self.__update_table_names()


    def get_table_prefix(self):
        """
        Returns the current database table prefix.
        
        @rtype:  string
        @return: The current prefix.
        """
        return self._table_prefix


    def _get_subtype_sql(self, column, objtypes):
        if type(objtypes) != type([]):
            objtypes = [objtypes]
        conds = []
        for objtype in objtypes:
            name = objtype.__name__
            if not self.is_registered(objtype):
                err = '%s must be passed to register_type() first' % name
                raise AttributeError(err)
            conds.append(column == name)
            conds += [column == t.__name__ for t in objtype.__subclasses__()]
        return sa.or_(*conds)


    def __register_type(self, objtype):
        self._types[objtype.__name__] = objtype


    def register_type(self, objtypes):
        """
        Before using any other methods you need to let Spiff Guard know what
        types (classes) you are using. For example, before being able to
        retrieve a resource from the database using get_resource(), you need
        to register the class using this function.

        @type  objtypes: class|list[class]
        @param objtypes: The class that you want to use with Spiff Guard.
        """
        if type(objtypes) != type([]):
            objtypes = [objtypes]
        for objtype in objtypes:
            self.__register_type(objtype)


    def is_registered(self, objtype):
        """
        Checks whether the given class is already registered.

        @rtype:  boolean
        @return: True if the given class is registered, False otherwise.
        """
        return self._types.has_key(objtype.__name__)


    def _action_cache_add(self, action):
        key = action.get_handle() + '/' + action.__class__.__name__
        self._action_cache[key] = action


    def __action_cache_get(self, handle, typename):
        key = handle + '/' + typename
        return self._action_cache.get(key, None)


    def _action_cache_flush(self, handle = None, typename = None):
        if handle is None or typename is None:
            self._action_cache.clear()
        else:
            key = handle + '/' + typename
            del self._action_cache[key]


    def _sql_cache_add(self, request, result):
        params = request.compile().construct_params()
        params = ['%s=%s' % (k, v) for k, v in params.iteritems()]
        sql    = '%s/%s' % (request, '/'.join(params))
        self._sql_cache[sql] = result


    def __sql_cache_get(self, request):
        params = request.compile().construct_params()
        params = ['%s=%s' % (k, v) for k, v in params.iteritems()]
        sql    = '%s/%s' % (request, '/'.join(params))
        result = self._sql_cache.get(sql, None)
        return result


    def _sql_cache_flush(self):
        self._sql_cache.clear()


    def __get_action_from_row(self, row):
        assert row is not None
        tbl_a  = self._table_map['action']
        type   = self._types[row[tbl_a.c.action_type]]
        key    = '%s/%s' % (tbl_a.c.handle, tbl_a.c.action_type)
        action = type(row[tbl_a.c.name], row[tbl_a.c.handle])
        action.set_id(row[tbl_a.c.id])
        self._action_cache_add(action)
        return action


    def __get_actions_from_query(self, query):
        """
        Returns a list of actions.
        """
        assert query is not None
        result = query.execute()

        # Collect all rows into an array.
        tbl_a       = self._table_map['action']
        action_list = []
        for row in result:
            action = self.__get_action_from_row(row)
            action_list.append(action)

        return action_list


    def get_action(self, **kwargs):
        """
        Like get_actions(), but
          - Returns None, if no match was found.
          - Returns the action, if exactly one match was found.
          - Raises an error if more than one match was found.

        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_actions().
        @rtype:  Action
        @return: The action or None.
        """
        # If the only argument is the handle, we try to fetch the action out
        # of the cache.
        if len(kwargs) == 2 \
          and kwargs.has_key('handle') \
          and kwargs.has_key('type'):
            action = self.__action_cache_get(kwargs.get('handle'),
                                             kwargs.get('type').__name__)
            if action is not None:
                return action

        result = self.get_actions(0, 2, **kwargs)
        if len(result) == 0:
            return None
        elif len(result) > 1:
            raise Exception('Too many results')
        return result[0]


    def get_actions(self, offset = 0, limit = 0, **kwargs):
        """
        Returns all actions that match the given criteria.
        
        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: The following keys may be used:
                         - id - the id of the action
                         - handle - the handle of the action
                         - type - the class type of the action
                       All values may also be lists (logical OR).
        @rtype:  list[Action]
        @return: The list of actions.
        """
        tbl_a = self._table_map['action']
        table = tbl_a
        where = None

        # ID.
        if kwargs.has_key('id'):
            ids      = kwargs.get('id')
            id_where = None
            if type(ids) == type(0):
                ids = [ids]
            for id in ids:
                id_where = sa.or_(id_where, tbl_a.c.id == id)
            where = sa.and_(where, id_where)

        # Handle.
        if kwargs.has_key('handle'):
            handles      = kwargs.get('handle')
            handle_where = None
            if type(handles) != type([]):
                handles = [handles]
            for handle in handles:
                handle_where = sa.or_(handle_where, tbl_a.c.handle == handle)
            where = sa.and_(where, handle_where)

        # Object type.
        if kwargs.has_key('type'):
            types = kwargs.get('type')
            cond  = self._get_subtype_sql(tbl_a.c.action_type, types)
            where = sa.and_(where, cond)

        select = table.select(where,
                              use_labels = True,
                              limit      = limit,
                              offset     = offset)
        return self.__get_actions_from_query(select)


    def __get_resource_from_row(self, row):
        if not row: return None
        tbl_r = self._table_map['resource']
        type  = self._types[row[tbl_r.c.resource_type]]
        #print "Type:", type
        resource = type(row[tbl_r.c.name], row[tbl_r.c.handle])
        resource.set_id(row[tbl_r.c.id])
        resource.set_n_children(row[tbl_r.c.n_children])
        resource._set_guard(self)
        return resource


    def __get_resources_from_query(self, query):
        """
        Returns a list of resources.
        """
        assert query is not None

        # Attempt to get the cached result first.
        result = self.__sql_cache_get(query)
        if result is not None:
            return result

        result = query.execute()
        row    = result.fetchone()
        if not row:
            self._sql_cache_add(query, [])
            return []

        tbl_r         = self._table_map['resource']
        tbl_a         = self._table_map['resource_attribute']
        last_id       = None
        resource_list = []
        while row is not None:
            last_id  = row[tbl_r.c.id]
            resource = self.__get_resource_from_row(row)
            resource_list.append(resource)
            if not resource:
                break

            # Append all attributes.
            while 1:
                self._read_attribute_from_row(row, resource)
                row = result.fetchone()
                if not row:
                    break
                if last_id != row[tbl_r.c.id]:
                    break

        self._sql_cache_add(query, resource_list)
        return resource_list


    def _read_attribute_from_row(self, row, resource):
        if row is None:
            return
        tbl_a = self._table_map['resource_attribute']
        try:
            type = row[tbl_a.c.type]
        except KeyError:
            return # Row has no attribute table joined in it.
        if type is None:
            value = None
        elif type == self.attrib_type_int:
            value = int(row[tbl_a.c.attr_int])
        elif type == self.attrib_type_bool:
            value = bool(row[tbl_a.c.attr_int])
        elif type == self.attrib_type_string:
            value = row[tbl_a.c.attr_string]
        if type is not None:
            resource.set_attribute(row[tbl_a.c.name], value)


    def _load_attribute(self, resource, name):
        tbl_a = self._table_map['resource_attribute']
        sel   = tbl_a.select(sa.and_(tbl_a.c.resource_id == resource.get_id(),
                                     tbl_a.c.name        == name),
                             limit = 1)
        res   = sel.execute()
        row   = res.fetchone()
        self._read_attribute_from_row(row, resource)


    def __get_resource_sql(self, offset = 0, limit = 0, **kwargs):
        tbl_r = self._table_map['resource']
        tbl_a = self._table_map['resource_attribute']
        table = tbl_r
        where = None

        # ID.
        if kwargs.has_key('id'):
            ids = kwargs.get('id')
            if type(ids) == type(0):
                ids = [ids]
            id_where = None
            for id in ids:
                id_where = sa.or_(id_where, tbl_r.c.id == id)
            where = sa.and_(where, id_where)

        # Handle.
        if kwargs.has_key('handle'):
            handles = kwargs.get('handle')
            if type(handles) != type([]):
                handles = [handles]
            handle_where = None
            for handle in handles:
                handle_where = sa.or_(handle_where, tbl_r.c.handle == handle)
            where = sa.and_(where, handle_where)

        # Name.
        if kwargs.has_key('name'):
            names = kwargs.get('name')
            if type(names) != type([]):
                names = [names]
            name_where = None
            for name in names:
                name_where = sa.or_(name_where, tbl_r.c.name == name)
            where = sa.and_(where, name_where)

        # Object type.
        if kwargs.has_key('type'):
            types = kwargs.get('type')
            cond  = self._get_subtype_sql(tbl_r.c.resource_type, types)
            where = sa.and_(where, cond)

        # Attributes.
        if kwargs.has_key('attribute'):
            table = tbl_r.outerjoin(tbl_a, tbl_r.c.id == tbl_a.c.resource_id)
            for attr, value in kwargs.get('attribute').iteritems():
                if type(value) == type(0):
                    where = sa.and_(where,
                                    tbl_a.c.type     == self.attrib_type_int,
                                    tbl_a.c.attr_int == int(value))
                elif type(value) == type(True):
                    where = sa.and_(where,
                                    tbl_a.c.type     == self.attrib_type_bool,
                                    tbl_a.c.attr_int == int(value))
                elif type(value) == type(''):
                    where = sa.and_(where,
                                    tbl_a.c.type        == self.attrib_type_string,
                                    tbl_a.c.attr_string == value)
                else:
                    raise Exception('Unknown attribute type %s' % type(value))
        elif offset == 0 and limit == 0:
            # If we are not filtering the attributes, and we are not limiting
            # the number of items, we may pull all attributes now.
            table = tbl_r.outerjoin(tbl_a, tbl_r.c.id == tbl_a.c.resource_id)

        return (table, where)


    def get_resource(self, **kwargs):
        """
        Like get_resources(), but
          - Returns None, if no match was found.
          - Returns the resource, if exactly one match was found.
          - Raises an error if more than one match was found.

        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_resources().
        @rtype:  Resource
        @return: The resource, or None if none was found.
        """
        result = self.get_resources(0, 2, **kwargs)
        if len(result) == 0:
            return None
        elif len(result) > 1:
            raise Exception('Too many results')
        return result[0]


    def has_resource(self, **kwargs):
        """
        Like get_resource(), but returns True if at least one result was
        found, False otherwise.
        Is significantly faster than get_resource.

        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_resources().
        @rtype:  boolean
        @return: True if the resource was found, False otherwise.
        """
        table, where = self.__get_resource_sql(**kwargs)
        tbl_r        = self._table_map['resource']
        sel          = sa.select([tbl_r.c.id],
                                 where,
                                 from_obj = [table],
                                 limit    = 1)
        result = sel.execute()
        if result.fetchone() is not None:
            return True
        return False


    def get_resources(self, offset = 0, limit = 0, **kwargs):
        """
        Returns a list of resources that match the given criteria.

        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: The following keys may be used:
                         id - the id of the resource
                         handle - the handle of the resource
                         type - the class type of the resource
                         attribute - a dict containing attribute/value pairs
        @rtype:  list[Resource]
        @return: The list of resources.
        """
        table, where = self.__get_resource_sql(offset, limit, **kwargs)
        select       = table.select(where,
                                    limit      = limit,
                                    offset     = offset,
                                    use_labels = True)
        return self.__get_resources_from_query(select)


    def get_resource_children(self,
                              parent_id,
                              offset = 0,
                              limit  = 0,
                              **kwargs):
        """
        Returns the list of children of the given parent that match the
        given criteria.

        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_resources().
        @rtype:  list[Resource]
        @return: The list of resources.
        """
        if parent_id is None:
            raise AttributeError('parent_id argument must not be None')
        if type(parent_id) != type(0):
            parent_id = parent_id.get_id()

        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        tbl_m  = self._table_map['path_ancestor_map']
        tbl_p2 = self._table_map['resource_path'].alias('p2')

        table, where = self.__get_resource_sql(**kwargs)
        table  = table.outerjoin(tbl_p1, tbl_r.c.id  == tbl_p1.c.resource_id)
        table  = table.outerjoin(tbl_m,  tbl_p1.c.id == tbl_m.c.resource_path_id)
        table  = table.outerjoin(tbl_p2, tbl_p2.c.id == tbl_m.c.ancestor_path_id)
        where  = sa.and_(where,
                         tbl_p2.c.resource_id == parent_id,
                         tbl_p1.c.depth == tbl_p2.c.depth + 1)

        select = table.select(where,
                              order_by   = [tbl_p1.c.resource_id],
                              use_labels = True,
                              limit      = limit,
                              offset     = offset)

        # Attempt to get the cached result first.
        children = self.__sql_cache_get(select)
        if children is not None:
            return children
        result = select.execute()

        # Collect all children.
        last     = None
        children = [];
        for row in result:
            if row[tbl_p1.c.resource_id] != last:
                last = row[tbl_p1.c.resource_id]
                resource = self.__get_resource_from_row(row)
                resource.set_n_children(row[tbl_r.c.n_children])
                children.append(resource)
            self._read_attribute_from_row(row, resource)

        self._sql_cache_add(select, children)
        return children


    def get_resource_parents(self,
                             child_ids,
                             offset = 0,
                             limit  = 0,
                             **kwargs):
        """
        Returns the list of parents of the given child that also match
        the given criteria.

        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_resources().
        @rtype:  list[Resource]
        @return: The list of resources.
        """
        if child_ids is None:
            raise AttributeError('child_ids argument must not be None')
        if type(child_ids) != type([]):
            child_ids = [child_ids]
        if len(child_ids) == 0:
            raise AttributeError('child_ids argument list is empty')

        tbl_r  = self._table_map['resource']
        tbl_a  = self._table_map['resource_attribute']
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        tbl_m  = self._table_map['path_ancestor_map']
        tbl_p2 = self._table_map['resource_path'].alias('p2')

        table, where = self.__get_resource_sql(**kwargs)
        table  = table.outerjoin(tbl_p1, tbl_r.c.id  == tbl_p1.c.resource_id)
        table  = table.outerjoin(tbl_m,  tbl_p1.c.id == tbl_m.c.ancestor_path_id)
        table  = table.outerjoin(tbl_p2, tbl_p2.c.id == tbl_m.c.resource_path_id)
        where  = sa.and_(where, tbl_p2.c.depth == tbl_p1.c.depth + 1)
        where2 = None
        for id in child_ids:
            if type(id) != type(0):
                id = id.get_id()
            where2 = sa.or_(where2, tbl_p2.c.resource_id == id)
        where = sa.and_(where, where2)

        select = table.select(where,
                              order_by   = [tbl_p1.c.resource_id],
                              use_labels = True,
                              limit      = limit,
                              offset     = offset)

        # Attempt to get the cached result first.
        parents = self.__sql_cache_get(select)
        if parents is not None:
            return parents
        result = select.execute()

        # Collect all parents.
        last    = None
        parents = [];
        for row in result:
            if row[tbl_p1.c.resource_id] != last:
                last = row[tbl_p1.c.resource_id]
                resource = self.__get_resource_from_row(row)
                resource.set_n_children(row[tbl_r.c.n_children])
                parents.append(resource)
            self._read_attribute_from_row(row, resource)

        self._sql_cache_add(select, parents)
        return parents


    def get_resource_path_from_id(self, id):
        """
        Returns an object representing the "path" of an object; that is, a
        list of ancestors, where the first item is the root of the path and
        the last item is the one with the given id.

        @rtype:  ResourcePath
        @return: The path to the item with the given id.
        """
        assert id is not None
        table  = self._table_map['resource_path']
        query  = sa.select([table.c.path],
                           table.c.resource_id == id,
                           from_obj = [table])
        result = query.execute()
        row    = result.fetchone()
        if not row:
            return None
        length = len(row['path'])
        list   = bin_path2list(row[table.c.path])
        return ResourcePath(list)


    def has_permission_from_id(self, actor_id, action_id, resource_id):
        """
        Check whether the actor with the given id has the permission to
        perform the action with the given id on the resource with the given
        id.

        @type  actor_id: int
        @param actor_id: The id of the resource that performs the action.
        @type  action_id: int
        @param action_id: The id of the action that is performed.
        @type  resource_id: int
        @param resource_id: The id of the resource on which the action is
                            performed.
        @rtype:  boolean
        @return: True if the permission is granted, False otherwise.
        """
        assert actor_id    is not None
        assert action_id   is not None
        assert resource_id is not None
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        tbl_m1 = self._table_map['path_ancestor_map'].alias('m1')
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        tbl_ac = self._table_map['acl']
        tbl_p3 = self._table_map['resource_path'].alias('p3')
        tbl_m2 = self._table_map['path_ancestor_map'].alias('m2')
        tbl_p4 = self._table_map['resource_path'].alias('p4')
        tbl = tbl_p1.outerjoin(tbl_m1, tbl_p1.c.id == tbl_m1.c.resource_path_id)
        tbl = tbl.outerjoin(tbl_p2, sa.or_(tbl_p2.c.id == tbl_p1.c.id,
                                           tbl_p2.c.id == tbl_m1.c.ancestor_path_id))
        tbl = tbl.outerjoin(tbl_ac, tbl_p2.c.resource_id == tbl_ac.c.resource_id)
        tbl = tbl.outerjoin(tbl_p3, tbl_p3.c.id == tbl_ac.c.actor_id)
        tbl = tbl.outerjoin(tbl_m2, tbl_p3.c.id == tbl_m2.c.ancestor_path_id)
        tbl = tbl.outerjoin(tbl_p4, sa.or_(tbl_p4.c.id == tbl_p3.c.id,
                                           tbl_p4.c.id == tbl_m2.c.resource_path_id))
        sel = sa.select([tbl_ac.c.permit],
                     sa.and_(tbl_p1.c.resource_id == resource_id,
                             tbl_ac.c.action_id   == action_id,
                             tbl_p4.c.resource_id == actor_id),
                     order_by   = [sa.desc(tbl_p2.c.depth), sa.desc(tbl_p3.c.depth)],
                     use_labels = True,
                     from_obj   = [tbl])

        result = sel.execute()
        row    = result.fetchone()
        #print "Searching: (%i, %i, %i)", (actor_id, action_id, resource_id)
        if row is None:
            return False
        return row[0]


    def has_permission(self, actor, action, resource):
        """
        Convenience wrapper around has_permission_from_id().

        @type  actor: Actor
        @param actor: The resource that performs the action.
        @type  action: int
        @param action: The action that is performed.
        @type  resource: int
        @param resource: The resource on which the action is performed.
        @rtype:  boolean
        @return: True if the permission is granted, False otherwise.
        """
        assert actor    is not None
        assert action   is not None
        assert resource is not None
        actor_id    = actor.get_id()
        action_id   = action.get_id()
        resource_id = resource.get_id()
        return self.has_permission_from_id(actor_id, action_id, resource_id)


    def get_permission_list_from_id(self,
                                    actor_id,
                                    offset = 0,
                                    limit  = 0,
                                    **kwargs):
        """
        Returns a list of ACLs that match the given criteria. The function
        ignores inheritance, so that ACLs are only returned if they were
        defined specificly for the requested resource.

        Allowed argument keywords include: action_id, resource_id,
        permit, action_type and resource_type.
        All keywords are optional; if no keywords are given all ACLs for
        the given actor_id are returned.

        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: The search criteria.
        @rtype:  list[Acl]
        @return: The list of ACLs.
        """
        # Get a list of all resources.
        tbl_p1 = self._table_map['resource_path'].alias('p1')

        # Search all ACLs that are defined for those resources.
        tbl_ac = self._table_map['acl']
        tbl = tbl_p1.outerjoin(tbl_ac, tbl_p1.c.resource_id == tbl_ac.c.resource_id)

        # Now search the corresponding actors.
        tbl_p3 = self._table_map['resource_path'].alias('p3')
        tbl = tbl.outerjoin(tbl_p3, tbl_p3.c.id == tbl_ac.c.actor_id)
        where = tbl_p3.c.resource_id == actor_id

        # Informative only.
        tbl_a1 = self._table_map['action'].alias('a1')
        tbl = tbl.outerjoin(tbl_a1, tbl_a1.c.id == tbl_ac.c.action_id)

        if kwargs.has_key('action_id'):
            where = sa.and_(where, tbl_ac.c.action_id == kwargs['action_id'])

        if kwargs.has_key('resource_id'):
            where = sa.and_(where, tbl_p1.c.resource_id == kwargs['resource_id'])

        if kwargs.has_key('permit'):
            where = sa.and_(where, tbl_ac.c.permit == kwargs['permit'])

        if kwargs.has_key('action_type'):
            types = kwargs.get('action_type')
            cond  = self._get_subtype_sql(tbl_a1.c.action_type, types)
            where = sa.and_(where, cond)

        if kwargs.has_key('resource_type'):
            tbl_r1 = self._table_map['resource'].alias('r1')
            tbl    = tbl.outerjoin(tbl_r1, tbl_r1.c.id == tbl_ac.c.resource_id)
            types  = kwargs.get('resource_type')
            cond   = self._get_subtype_sql(tbl_r1.c.resource_type, types)
            where  = sa.and_(where, cond)

        sel = sa.select([tbl_ac.c.id,
                         tbl_ac.c.actor_id,
                         tbl_ac.c.resource_id,
                         tbl_ac.c.permit,
                         tbl_a1.c.id,
                         tbl_a1.c.name,
                         tbl_a1.c.handle],
                        where,
                        order_by   = [tbl_p3.c.path, tbl_p1.c.path],
                        use_labels = True,
                        limit      = limit,
                        offset     = offset,
                        from_obj   = [tbl])

        # Collect all permissions.
        result   = sel.execute()
        acl_list = [];
        for row in result:
            action = Action(row[tbl_a1.c.name], row[tbl_a1.c.handle])
            action.set_id(row[tbl_a1.c.id])
            acl = Acl(row[tbl_ac.c.actor_id],
                      action,
                      row[tbl_ac.c.resource_id],
                      row[tbl_ac.c.permit])
            acl.set_id(row[tbl_ac.c.id])
            acl_list.append(acl)

        return acl_list


    def _get_permission_list_with_inheritance_tables(self, **kwargs):
        """
        Returns a tuple, where the first element is the join of tables
        for get_permission_list_from_id_with_inheritance and
        get_last_permission_change, and the second element is the WHERE
        clause. All other elements are single tables from the join.
        """
        # Looking to find a bug in this function? Congratulations, you are
        # about to enter hell. If you manage to find (and fix) that damn
        # bug you are officially a hero.
        # But don't blame me for this code, because any database design
        # will suck in at least one respect when you implement ACLs.
        where = None

        # Get all actor paths.
        tbl_p1 = self._table_map['resource_path'].alias('p1')
        if kwargs.has_key('actor_id'):
            actor_id = kwargs['actor_id']
            where    = sa.and_(where, tbl_p1.c.resource_id == actor_id)

        # All paths that are a parent of the path.
        tbl_m1 = self._table_map['path_ancestor_map'].alias('m1')
        tbl = tbl_p1.outerjoin(tbl_m1, tbl_p1.c.id == tbl_m1.c.resource_path_id)

        # Still all paths that are a child of the direct match, and also the
        # direct match itself.
        tbl_p2 = self._table_map['resource_path'].alias('p2')
        tbl = tbl.outerjoin(tbl_p2, sa.or_(tbl_p2.c.id == tbl_p1.c.id,
                                           tbl_p2.c.id == tbl_m1.c.ancestor_path_id))

        # All ACLs that reference the given actor or any of its parents.
        tbl_ac1 = self._table_map['acl'].alias('ac1')
        tbl = tbl.outerjoin(tbl_ac1, tbl_p2.c.resource_id == tbl_ac1.c.actor_id)
        if kwargs.has_key('permit'):
            where  = sa.and_(where, tbl_ac1.c.permit == kwargs['permit'])

        # Path of the resource that is referenced by the ACL.
        tbl_p3 = self._table_map['resource_path'].alias('p3')
        tbl = tbl.outerjoin(tbl_p3, tbl_p3.c.resource_id == tbl_ac1.c.resource_id)

        # Paths of all children of the resource.
        tbl_m2 = self._table_map['path_ancestor_map'].alias('m2')
        tbl = tbl.outerjoin(tbl_m2, tbl_p3.c.id == tbl_m2.c.ancestor_path_id)

        # Paths of all children of the resource, and also the resource itself.
        tbl_p4 = self._table_map['resource_path'].alias('p4')
        tbl = tbl.outerjoin(tbl_p4, sa.or_(tbl_p4.c.id == tbl_p3.c.id,
                                           tbl_p4.c.id == tbl_m2.c.resource_path_id))
        if kwargs.has_key('resource_id'):
            where = sa.and_(where, tbl_p4.c.resource_id == kwargs['resource_id'])

        # Informative only.
        tbl_a1 = self._table_map['action'].alias('a1')
        tbl = tbl.outerjoin(tbl_a1, tbl_a1.c.id == tbl_ac1.c.action_id)
        if kwargs.has_key('action_id'):
            action_id = kwargs['action_id']
            where     = sa.and_(where, tbl_a1.c.id == action_id)
        if kwargs.has_key('action_type'):
            types = kwargs.get('action_type')
            cond  = self._get_subtype_sql(tbl_a1.c.action_type, types)
            where = sa.and_(where, cond)

        # Informative only.
        if kwargs.has_key('resource_type'):
            tbl_r1 = self._table_map['resource'].alias('r1')
            tbl    = tbl.outerjoin(tbl_r1, tbl_r1.c.id == tbl_p4.c.resource_id)
            types  = kwargs.get('resource_type')
            cond   = self._get_subtype_sql(tbl_r1.c.resource_type, types)
            where  = sa.and_(where, cond)

        # Informative only.
        if kwargs.has_key('actor_type'):
            tbl_r2 = self._table_map['resource'].alias('r2')
            tbl    = tbl.outerjoin(tbl_r2, tbl_r2.c.id == tbl_p2.c.resource_id)
            types  = kwargs.get('resource_type')
            cond   = self._get_subtype_sql(tbl_r2.c.resource_type, types)
            where  = sa.and_(where, cond)

        # Get all ACLs that control the same resource/action as the ACL above.
        tbl_ac2 = self._table_map['acl'].alias('ac2')
        tbl = tbl.outerjoin(tbl_ac2, sa.and_(tbl_ac1.c.action_id   == tbl_ac2.c.action_id,
                                             tbl_ac1.c.resource_id == tbl_ac2.c.resource_id))
        
        # Get a list of all the actors that perform the action.
        tbl_p5 = self._table_map['resource_path'].alias('p5')
        tbl = tbl.outerjoin(tbl_p5, tbl_ac2.c.actor_id == tbl_p5.c.resource_id)

        # Make sure that the actor is a parent of the wanted one.
        tbl_m3 = self._table_map['path_ancestor_map'].alias('m3')
        tbl = tbl.outerjoin(tbl_m3, tbl_p5.c.id == tbl_m3.c.ancestor_path_id)
        
        # Get the list of all the children.
        tbl_p6 = self._table_map['resource_path'].alias('p6')
        tbl = tbl.outerjoin(tbl_p6, sa.or_(tbl_m3.c.resource_path_id == tbl_p6.c.id,
                                           tbl_p5.c.id               == tbl_p6.c.id))
        if kwargs.has_key('actor_id'):
            actor_id = kwargs['actor_id']
            where    = sa.and_(where, tbl_p6.c.resource_id == actor_id)

        return tbl, where, tbl_ac1, tbl_a1, tbl_p1, tbl_p2, tbl_p4, tbl_p5


    def get_permission_list_from_id_with_inheritance(self,
                                                     offset = 0,
                                                     limit  = 0,
                                                     **kwargs):
        """
        Returns a list of ACLs that match the given criteria. The function
        honors inheritance, so that ACLs are returned even if they were
        defined for a parent of the requested resource.

        This function is expensive and should be used with care.
        You might want to consider using get_permission_list_from_id()
        instead.
        
        Allowed argument keywords include: actor_id, action_id, resource_id,
        permit, actor_type, action_type and resource_type.
        All arguments are optional; if no arguments are given all ACLs are
        returned.

        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: The search criteria.
        @rtype:  list[Acl]
        @return: The list of ACLs.
        """
        tbl,     \
        where,   \
        tbl_ac1, \
        tbl_a1,  \
        tbl_p1,  \
        tbl_p2,  \
        tbl_p4,  \
        tbl_p5   = self._get_permission_list_with_inheritance_tables(**kwargs)
        group_by = [tbl_ac1.c.actor_id,
                    tbl_ac1.c.action_id,
                    tbl_ac1.c.resource_id]
        sel = sa.select([tbl_ac1.c.id,
                         tbl_ac1.c.actor_id,
                         tbl_ac1.c.resource_id,
                         tbl_ac1.c.permit,
                         tbl_a1,
                         tbl_p1.c.resource_id,
                         tbl_p2.c.depth.label('p2_depth'),
                         sa.func.max(tbl_p5.c.depth).label('p5_max_depth')],
                        where,
                        from_obj   = [tbl],
                        use_labels = True,
                        limit      = limit,
                        offset     = offset,
                        group_by   = group_by,
                        having     = 'p2_depth = p5_max_depth',
                        order_by   = [tbl_p2.c.path, tbl_p4.c.path])

        # Collect all permissions.
        #print sel
        result   = sel.execute()
        acl_list = []
        for row in result:
            #print row
            action = Action(row[tbl_a1.c.name], row[tbl_a1.c.handle])
            action.set_id(row[tbl_a1.c.id])
            acl = Acl(row[tbl_ac1.c.actor_id],
                      action,
                      row[tbl_ac1.c.resource_id],
                      row[tbl_ac1.c.permit],
                      row[tbl_p1.c.resource_id] != row[tbl_ac1.c.actor_id])
            acl.set_id(row[tbl_ac1.c.id])
            acl_list.append(acl)
        
        #print "LENGTH:", len(acl_list)
        return acl_list


    def get_last_permission_change(self, **kwargs):
        """
        Returns the time of the last permission change that affected any
        resource that matches the given argument.
        
        Allowed argument keywords include: actor_id, action_id, resource_id,
        permit, actor_type, action_type and resource_type.
        All arguments are optional; if no arguments are given all ACLs are
        returned.

        @type  kwargs: dict
        @param kwargs: The search criteria.
        @rtype:  datetime.datetime
        @return: The latest ACL change.
        """
        tbl,     \
        where,   \
        tbl_ac1, \
        tbl_a1,  \
        tbl_p1,  \
        tbl_p2,  \
        tbl_p4,  \
        tbl_p5   = self._get_permission_list_with_inheritance_tables(**kwargs)
        group_by = [tbl_ac1.c.actor_id,
                    tbl_ac1.c.action_id,
                    tbl_ac1.c.resource_id]
        sel = sa.select([tbl_ac1.c.last_change.label('last_change'),
                        tbl_p2.c.depth.label('p2_depth'),
                        sa.func.max(tbl_p5.c.depth).label('p5_max_depth')],
                     where,
                     from_obj   = [tbl],
                     use_labels = True,
                     group_by   = group_by,
                     having     = 'p2_depth = p5_max_depth',
                     order_by   = [tbl_p2.c.path, tbl_p4.c.path])
        sel = sel.alias('permission_changes')
        sel = sa.select([sa.func.max(sel.c.last_change).label('last_change')])
        sel = sa.select([tbl_ac1.c.last_change])

        result = sel.execute()
        row    = result.fetchone()
        return row.last_change


    def get_permission_list_with_inheritance(self,
                                             offset = 0,
                                             limit  = 0,
                                             **kwargs):
        """
        Returns a list of ACLs that match the given criteria. Allowed argument
        keywords include: actor, action, resource, permit, actor_type,
        action_type and resource_type.
        All arguments are optional.

        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: The search criteria.
        @rtype:  list[Acl]
        @return: The list of ACLs.
        """
        if kwargs.has_key('actor'):
            kwargs['actor_id'] = kwargs['actor'].get_id()

        if kwargs.has_key('action'):
            kwargs['action_id'] = kwargs['action'].get_id()

        if kwargs.has_key('resource'):
            kwargs['resource_id'] = kwargs['resource'].get_id()

        return self.get_permission_list_from_id_with_inheritance(limit,
                                                                 offset,
                                                                 **kwargs)
