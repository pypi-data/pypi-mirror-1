import sqlalchemy.sql as sql

import pdw.model as model

main_classes = [ model.Item, model.Work, model.Person ]

def basic_info():
    results = {
        u'count': {},
        u'work type': None, 
        }
    for cls in main_classes:
        results['count'][cls.__name__] = cls.query.count()
    tresults = [['Object', 'Work Type', 'Count']]
    for cls in [ model.Item, model.Work ]:
        for thetype in [ model.WORK_TYPES.text,  model.WORK_TYPES.composition,
                model.WORK_TYPES.recording ]:
            val = cls.query.filter_by(type=thetype).count()
            tresults.append([cls.__name__, thetype, val])
    results[u'work type'] = tresults
    return results


default_years = range(1800, 2010, 10)
def by_year(query, year_field, years=default_years):
    cumulative = []
    for year in years:
        todate = query.filter(year_field<=year).count()
        cumulative.append(todate)
    return (years, cumulative)

def cumulative_to_per_period(cumulative):
    out = [ cumulative[0] ]
    out += [ cumulative[x+1] - cumulative[x] for x in range(len(cumulative)-1)
            ]
    return out


def persons_by_item_counts(howmany=1000):
    x = '''SELECT person.name, ...
    FROM 
    GROUP BY item_2_person.person_id
    ORDER BY count(*) DESC
    '''
    fromobj = model.person_table.join(model.item_2_person)
    pt = model.person_table
    i2pt = model.item_2_person
    q = sql.select([pt.c.id, pt.c.name, sql.func.count('*'), i2pt.c.person_id],
            from_obj=fromobj
            )
    q = q.group_by(model.item_2_person.c.person_id)
    q = q.order_by(sql.func.count('*'))
    q = q.limit(howmany)
    return q

