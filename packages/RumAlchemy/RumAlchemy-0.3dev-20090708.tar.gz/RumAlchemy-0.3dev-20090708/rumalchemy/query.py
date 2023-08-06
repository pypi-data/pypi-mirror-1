# -*- coding: utf-8 -*-

from sqlalchemy import sql
from rum import query as rumquery
from rum.genericfunctions import generic

from rumalchemy.util import get_mapper, primary_key_property_names,\
    get_dialect_name
from re import sub
_escape_char="0"
def _escape_pattern(p):
    p=p.replace(_escape_char,2*_escape_char)
    pattern=r'(%|_)'
    rep=_escape_char+r'\g<1>'
    return sub(pattern,rep,p)

class SAQuery(rumquery.Query):
    """Creates SA queries"""

    def filter(self, query):
        assert self.resource
        if self.expr is not None:
            query = self._apply_expression(query)
        self.count = query.count()
        if self.sort is not None:
            query = self._apply_sort(query)
        else:
            query=self.apply_default_ordering(query)
        if self.limit is not None:
            query = self._apply_limit(query)
        if self.offset is not None:
            query = self._apply_offset(query)
        query = self.set_query_options(query)
        return query

    @generic
    def apply_default_ordering(self,query):
        """applies a default ordering to query"""
        pass
        
    @generic
    def remap_sort_column(self, col):
        pass
    
    @remap_sort_column.when()
    def _default_criterium_for_field(self, col):
        return col
        
    apply_default_ordering.when()
    def _apply_default_ordering(self, query):
        r=self.resource
        return query.order_by(*[getattr(r,n) for n in primary_key_property_names(r)])
        
    @generic
    def set_query_options(self, query):
        """Apply sqlalchemy options like eagerload to query"""
    
    set_query_options.when()
    def __default_query_options(self, query):
        return query
    def _apply_offset(self, query):
        return query.offset(self.offset)

    def _apply_limit(self, query):
        return query.limit(self.limit)

    def _apply_sort(self, query):
        r = self.resource
        return query.order_by(*[
            getattr(sql, s.name)(getattr(r, 
            self.remap_sort_column(s.col)))
            for s in self.sort
            ])

    def _apply_expression(self, query):
        return query.filter(translate(self.expr, self.resource))

rumquery.QueryFactory.register(SAQuery, pred="get_mapper(resource) is not None")
apply_default_ordering=SAQuery.apply_default_ordering.im_func
set_query_options=SAQuery.set_query_options.im_func


lower = sql.func.lower

@generic
def translate(expr, resource):
    """
    Translate a :meth:`rum.query.Expression` into an sqlalchemy sql expression.
    """

@generic 
def normalize(expr):
    "Normalize expression to some standard form"


@normalize.when()
def _lower_case(expr):
    return lower(expr)

@normalize.when("get_dialect_name().lower().startswith('postgres')")
def _lower_and_accents(string):
    translate=sql.func.translate
    replace=sql.func.replace
    return replace(translate(lower(string),'äöüáéíóúàèìòùyw','aouaeiouaeiouiv'),'ß','ss')
@translate.when((rumquery.eq,))
def _eq(expr, resource):
    return getattr(resource, expr.col) == expr.arg

@translate.when((rumquery.neq,))
def _neq(expr, resource):
    return getattr(resource, expr.col) != expr.arg

@translate.when((rumquery.contains,))
def _in(expr, resource):
    pattern = _escape_pattern(expr.arg)
    return normalize(getattr(resource, expr.col)).contains(normalize(pattern), escape=_escape_char)

@translate.when((rumquery.startswith,))
def _startswith(expr, resource):
    pattern = _escape_pattern(expr.arg)
    return normalize(getattr(resource, expr.col)).startswith(normalize(pattern), escape=_escape_char)

@translate.when((rumquery.endswith,))
def _endswith(expr, resource):
    pattern = _escape_pattern(expr.arg)
    return normalize(getattr(resource, expr.col)).endswith(normalize(pattern), escape=_escape_char)

@translate.when((rumquery.and_,))
def _and(expr, resource):
    return sql.and_(*[translate(e, resource) for e in expr.col])

@translate.when((rumquery.or_,))
def _or(expr, resource):
    return sql.or_(*[translate(e, resource) for e in expr.col])

@translate.when((rumquery.lt,))
def _lt(expr, resource):
    return getattr(resource, expr.col) < expr.arg

@translate.when((rumquery.lte,))
def _lte(expr, resource):
    return getattr(resource, expr.col) <= expr.arg

@translate.when((rumquery.gt,))
def _gt(expr, resource):
    return getattr(resource, expr.col) > expr.arg

@translate.when((rumquery.gte,))
def _gte(expr, resource):
    return getattr(resource, expr.col) >= expr.arg

@translate.when(
    "isinstance(expr, rumquery.not_) and isinstance(expr.col, basestring)")
def _not_col_name(expr, resource):
    return sql.not_(getattr(resource, expr.col))

@translate.when(
    "isinstance(expr, rumquery.not_) and "
    "isinstance(expr.col, rumquery.Expression)")
def _not_expr(expr, resource):
    return sql.not_(translate(expr.col, resource))

@translate.when((rumquery.notnull,))
def _notnull(expr, resource):
    return getattr(resource, expr.col) != None

@translate.when((rumquery.null,))
def _null(expr, resource):
    return getattr(resource, expr.col) == None

@translate.when((rumquery.in_,))
def _in(expr, resource):
    return getattr(resource, expr.col).in_(expr.arg)

remap_sort_column = SAQuery.remap_sort_column.im_func