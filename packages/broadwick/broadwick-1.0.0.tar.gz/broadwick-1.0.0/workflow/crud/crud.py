from broadwick.web.utils import expose_genshi, request_param
from sets import Set
from twisted.web import static
from sqlalchemy.orm.util import class_mapper
import os
import time
import datetime
import logging


def resource_path(f=None):
    path = os.path.dirname(os.path.abspath(__file__))
    if f:
        path = os.path.join(path, f)
    return path


class Model():
    
    def __init__(self, base, instance):
        self._base = base
        self._mapper = class_mapper(base, compile=False)
        self.name = base.__name__
        self.instance = instance
        self.cols = [p.key for p in self._mapper.iterate_properties]
        self.fkeys = []
        self.oTms = []
        self.mTms = []
        
    def items(self, session):
        return session.query(self._base).all()
        
    


class Crud(object):
    
    def __init__(self, base=None, display=None):        
        self.images =  static.File(resource_path('images'))
        if display:
            self._display = display
        self._base = base
        self._tables = base._decl_class_registry.keys()
        
    
    @expose_genshi(template=resource_path('crud.genshi'))
    @request_param('_request')
    def index(self, _request=None, _action=None, _table=None, _join=None, _related=None, id=None, _id=None, **kwargs):
        session = _request.sa_session
        logging.info('%s %s %s %s %r %r' % (_action, _table, id, _id, _related, kwargs))
        tables = self._tables
        tables.sort()
        if _table is None:
            _table = tables[0]
        id = id and int(id) or None
        edit = id and session.query(self._table_by_name(_table)).get(id) or None
        table = self._table_by_name(_table)
        joinmodel = joinedit = errors = None
        if edit and self._hasJoins(_table):
            if _join is None:
                _join = table.sqlmeta.joins[0]
            else:
                for jdef in table.sqlmeta.joins:
                    if jdef.joinDef.name == _join:
                        _join = jdef
                        break
            joinmodel = self._table_by_name(_join.joinDef.kw['otherClass'])
            _id = _id and int(_id) or None
            joinedit = _id and joinmodel.get(_id) or None
        if _action == 'add': 
            logging.info('adding %r' % kwargs)
            errors, values = self._validate(table, kwargs)
            if errors == {}:
                edit = table(**values)
                id = edit.id            
        elif _action == 'save':
            logging.info('saving %r' % kwargs)
            errors, values = self._validate(table, kwargs)
            if errors=={}:
                edit.set(**values)
        elif _action == 'delete':
            logging.info('deleting %r' % kwargs)
            edit.destroySelf()
            edit = None
            id = None
        elif _action=='relate':
            related = isinstance(_related, list) and _related or isinstance(_related, str) and [_related] or []
            has = Set(getattr(edit, _join.joinDef.name))
            should = Set([joinmodel.get(x) for x in related])
            for item in has - should:
                getattr(edit, 'remove%s' % _join.addRemoveName)(item)
            for item in should - has:
                getattr(edit, 'add%s' % _join.addRemoveName)(item)
        elif _action == 'append':
            logging.info('appending %r' % kwargs)
            errors, values = self._validate(joinmodel, kwargs)
            if errors == {}:
                joinedit = joinmodel(**values)
                _id = joinedit.id       
        elif _action == 'update':
            logging.info('updating %r' % kwargs)
            errors, values = self._validate(joinmodel, kwargs)
            if errors == {}:
                joinedit.set(**values)
        elif _action == 'remove':
            logging.info('removing %r' % kwargs)
            joinedit.destroySelf()
            joinedit = None
            _id = None    
        return {'model': Model(table, edit),
                'tables': tables,
                'id': id,
                'edit': edit,
                'fkey_display': self._display,
                'join' : _join,
                'joinmodel': joinmodel,
                'joinedit': joinedit,
                '_id': _id,
                'errors': errors,
                'session': session }
        
    def _table_by_name(self, name):
        return self._base._decl_class_registry[name]
    
    def _has_joins(self, table):
        return False
    
    def _display(self, o):
        return o

    def _validate(self, table, data ):
        DATETIMEFORMAT = '%Y-%m-%d %H:%M:%S'
        DATEFORMAT = '%Y-%m-%d'
        TIMEFORMAT = '%H:%M:%S'
        errors = {}
        values = {}
#        for col in table.sqlmeta.columnList:
#            try:
#                if col.notNone and data.get(col.name) in [None,'']:
#                    errors[col.name]='%s cannot be empty!' % col.name
#                elif data.get(col.name):
#                    if isinstance(col, SOTimeCol):
#                        value = data.get(col.name)
#                        try:
#                            values[col.name] = datetime.time(*time.strptime(value,TIMEFORMAT)[3:6])
#                        except Exception, ex:
#                            logging.warn(ex)
#                            errors[col.name]='excepted time[%s]' % TIMEFORMAT.replace('%','')                        
#                    elif isinstance(col, SODateTimeCol):
#                        value = data.get(col.name)
#                        format = len(value)==10 and DATEFORMAT or DATETIMEFORMAT
#                        try:
#                            values[col.name] = datetime.datetime(*time.strptime(value,format)[0:6])
#                        except Exception:
#                            errors[col.name]='excepted date[%s]' % format.replace('%','')
#                    elif isinstance(col, SOBoolCol):
#                        values[col.name] = 'True' == data.get(col.name)
#                        data[col.name] = values[col.name]
#                    elif isinstance(col, SOFloatCol):
#                        values[col.name] = float(data.get(col.name))
#                    else:
#                        values[col.name] = data.get(col.name)
#            except Exception, ex:
#                errors[col.name]=str(ex)
        return errors, values
                