'''Encapsulate standard non-trivial search/match actions.

Remarks on Matching
===================

When we match item X from DB A -> DB B

1. simplify not at all then match
2. simplify a bit more then match
3. simplify a lot then match

Work generation:
    * Remove item type information
'''
import sqlalchemy.sql as sql

import pdw.model as model
import pdw.name

class QueryHelper:

    @classmethod
    def item_person(self, depth=1):
        q = model.item_table.join(model.item_2_person).join(model.person_table)
        return q

    @classmethod
    def work_person(self, depth=1):
        q = model.work_table.join(model.work_2_person).join(model.person_table)
        return q

    @classmethod
    def join_extras(self, query, key, table_object, extra_alias=None):
        '''
        Use outer join for this so that multiple joins can be made to the
        extras table.

        @param extra_alias: alias for extra table (needed if joining multiple times)
        '''
        if extra_alias:
            et = extra_alias
        else:
            et = model.extra_table

        newq = query.outerjoin(et,
            sql.and_(et.c.table==unicode(table_object.name),
                et.c.key==key,
                et.c.fkid==table_object.c.id
                )
            )
        return newq

    @classmethod
    def by_name(self, query, name):
        exact = query.filter(model.person_table.c.name.ilike(name))
        return exact

    @classmethod
    def by_name_inexact(self, query, name):
        inexact = query.filter(model.person_table.c.name.ilike(name + '%'))
        return inexact

    @classmethod
    def by_name_inexact2(self, query, name):
        inexact2 = query.filter(
                model.person_table.c.name.ilike('%' + name + '%')
                )
        return inexact2
    
    @classmethod
    def _by_title(self, query, title, tableobj, exact=True):
        if exact:
            exact = query.filter(tableobj.c.title==title)
            return exact
        else:
            simple = Titlizer.simplify_for_search(title)
            inexact = query.filter(tableobj.c.title.ilike('%' + simple  + '%'))
            return inexact

    @classmethod
    def by_work_title(self, query, title, exact=True):
        # simplify title here?
        return self._by_title(query, title, tableobj=model.work_table,
                exact=exact)

    @classmethod
    def by_item_title(self, query, title, exact=True):
        return self._by_title(query, title, tableobj=model.item_table,
                exact=exact)


class Finder(object):
    def __init__(self):
        self.info = []
        self.score = 0

    def person(self, name, work_title=None, strictness=0):
        '''
        Returns best match
        @name: Person\'s name to search for
        @work_title: currently ignored
        @strictness: currently ignored
        @return: record giving best match, or None if failure
        '''
        exact = QueryHelper.by_name(model.Person.query, name)
        inexact = QueryHelper.by_name_inexact(model.Person.query, name)
        inexact2 = QueryHelper.by_name_inexact2(model.Person.query, name)
        for q in [ exact, inexact, inexact2 ]:
            out = q.limit(2).all()
            if len(out) == 1:
                return out[0]
            elif len(out) == 2:
                self.score -= 1
                return out[0]
            else:
                self.score -= 5
        return None

    def work(self, title, authors=None, strict=True):
        if not authors: authors = [] # cannot use [] as a default item

        # we do not need to join if not authors
        q = model.Work.query
        exact = QueryHelper.by_work_title(q, title)
        # inexact = QueryHelper.by_work_title(q, title, exact=False)

        # how exactly does join work, may need to search by one author at time
        for name in authors:
            # exact = exact.join(model.
            # model.Work.query.join(['contributors', 'person'])
            exact = exact.filter(model.Person.name.ilike(name + '%'))
            inexact = exact.filter(model.Person.name.ilike(name + '%'))
        out = exact.limit(5).all()
        if len(out) == 0:
            if strict:
                return None
            else:
                self.score -= 5
                out = inexact.limit(5).all()
        if len(out) == 0:
            return None
        elif len(out) == 1:
            return out[0]
        else: # TODO: search more carefully
            return out[0]

    def get_work_for_item(self, item):
        '''Find associated work.
        '''
        if not item.title:
            return None
        titlizer = Titlizer()
        # simplify_for_search ...
        work_title = titlizer.simplify(item.title) 
        outwork = self.work(work_title, strict=True)
        return outwork

    def create_work_for_item(self, item):
        work_title = titlizer.simplify(item.title) 
        return model.Work(title=work_title)


class Titlizer:
    @classmethod
    def norm(self, title):
        '''Basis normalization (do not remove or add anything).
        '''
        title = unicode(title.strip())
        tmptitle = title.lower()
        if tmptitle.startswith('a '):
            title = title[2:] + ', A'
        elif tmptitle.startswith('the '):
            title = title[2:] + ', The'
        # TODO: do this generally with regex?
        title = title.replace(',A', ', A')
        title = title.replace(', The', ', The')
        if title.endswith(',The'): title = title[:-4]
        # ? messes up things like A and 'Tis 
        # title = title.capitalize()
        return title

    @classmethod
    def simplify(self, title):
        '''Simplify title in various ways and then norm.
        '''
        # TODO: regexize this ...
        title = title.split(':')[0]
        title = title.replace('"', '')
        title = self.norm(title)
        return title

    @classmethod
    def simplify_for_search(self, title):
        '''Simplify even more (remove trailing A and The, problematic
        punctuation etc.
        '''
        title = self.simplify(title)
        if title.endswith(', A'): title = title[:-3]
        if title.endswith(', The'): title = title[:-5]
        title = title.replace('!', '') 
        title = title.replace('?', '') 
        return title

