'''Consolidate persons, items, works etc.

Two options:

    1. Consolidate on load
    2. Consolidate post load

2 is more powerful as we have full information when consolidating but 1 might
be simpler (?). Decision: Focus on 2 for time being.

1. Do some summary statistics (how many duplicate names do we have etc)
2. Consolidation by:
    * person
    * item (work generation)

Person Algorithm:
    * Consolidate all people with same name + dates
        * Exceptions (blanks, anonymous)
    * Work generation. Title + author 
        * Title normalization

Asides:
    * Info on dataset type/source is important e.g. MARC datasets are supposed
      to have unique name + dates
    * For development we will need a test dataset we can reload fairly easily
    * For recordings do not bother with work for recording itself (atm)
    * Generating test data:
        * Do it by hand (preferred option for time being)
        * Take a raw dataset and dump one person with a lot of duplicates
'''

import sqlalchemy.sql as sql
import pdw.model as model

def consolidate_persons(verbose=False):
    duplicates_sql_query = """SELECT name, birth_date, count(*), srcid FROM person 
    WHERE name != '' AND name is not null AND birth_date is not NULL AND
    birth_date != 'None'
    GROUP BY name, birth_date
    HAVING count(*) > 1
    ORDER BY count(*) DESC;
    """
    myq = sql.text(duplicates_sql_query)
    engine = model.metadata.bind
    duplicates_query = engine.execute(myq)
    for dup in duplicates_query:
        if verbose: print dup
        name, birth_date = dup[:2]
        dup_persons = model.Person.query.filter_by(name=name, birth_date=birth_date) 
        surviving_person = dup_persons.first()
        for dup_person in dup_persons[1:]:
            for item in dup_person.items:
               item.persons.append(surviving_person)
            dup_person.items = []
            for work in dup_person.works:
                work.persons.append(surviving_person)
            dup_person.works = []
            model.Session.delete(dup_person)
        model.Session.commit()
        model.Session.clear()


import pdw.search
def items_to_works(verbose=True, query=None):
    '''
    ASSUME: persons already consolidated

    1. [Optional] For all items not having a work
    2. Group by:
        * item title (normalized), person
    3. Does there already exist a work to match to?
    4. If not generate a new work (with a normalized title)

    Then reverse process query by normalized work title ...

    For those items with no duplicates do we both matching to generate a work?

    Assume for present none with a work id
    '''
    # TODO: allow for limiting coverage to those items in query
    
    pt = model.person_table
    it = model.item_table
    wt = model.work_table
    q = sql.select([it.c.title, pt.c.id, pt.c.name, sql.func.count('*')],
            from_obj=pdw.search.QueryHelper.item_person()
            )
    q = q.group_by([it.c.title, pt.c.id])
    q = q.having(sql.func.count('*')>1)
    q = q.order_by(sql.func.count('*'))
    sqlq = '''SELECT item.title, person.id, person.name, count(*), person.id FROM
    item JOIN item_2_person on item.id = item_2_person.item_id
    JOIN person on person.id = item_2_person.person_id
    GROUP BY item.title, person.id
    HAVING count(*) > 1
    ORDER BY count(*) DESC
    '''
    myq = sql.text(sqlq)
    engine = model.metadata.bind
    for dup in engine.execute(myq):
        if verbose: print dup
        title, pid = dup[:2]
        q = pdw.search.QueryHelper.item_person()
        q = q.select().where(it.c.title==title).where(pt.c.id==pid)
        # q = model.Item.query.join('contributors').join('person')
        # q = q.filter(model.Item.title==title).where(model.Person.id==id)
        # TODO: have a work already? (if so select first one)
        # TODO: ? should we check if have different works assigned already? 
        titems = q.execute().fetchall()
        repr_item = model.Item.query.get(titems[0][it.c.id])
        # what happens if title is None or ''
        # do we want to simplify or norm?
        simple_title = pdw.search.Titlizer.simplify(title)
        finder = pdw.search.Finder()

        # what about when multiple matching works?
        workq = pdw.search.QueryHelper.work_person().select()
        workq = workq.where(wt.c.title==simple_title)
        if pid: # what do we if no person?
            workq = workq.where(pt.c.id==pid)
        existing_work = workq.execute().fetchone()
        if existing_work:
            work = model.Work.query.get(existing_work[wt.c.id])
        else:
            work = model.Work(title=simple_title)
            work.persons = [ p for p in repr_item.persons ]
        # TODO: set date based on earliest item ... ?
        for itemrow in titems:
            item = model.Item.query.get(itemrow[it.c.id])
            # What about if it already has a work?
            if not work in item.works:
                item.works.append(work)
        model.Session.commit()

# TODO: separate checking items with works already
# TODO: works and subworks (e.g. Winterreise)
# Duplicate items ????
