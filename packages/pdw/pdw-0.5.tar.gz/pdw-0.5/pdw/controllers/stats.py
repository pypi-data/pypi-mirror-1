from pdw.lib.base import *

import pdw.model
import pdw.stats as stats

class StatsController(BaseController):

    def index(self):
        c.basic = stats.basic_info()
        c.count_table = [
            [ k for k in c.basic['count'] ],
            [ v for v in c.basic['count'].values() ]
        ]
        import swiss
        td = swiss.TabularData.from_list(c.basic['work type'])
        print td.header
        td = swiss.pivot(td, 'Work Type', 'Object', 'Count')
        c.by_type_table = td.to_list()
        print c.by_type_table

        c.by_year_table = [ ['Year', 'No. of Works', 'No. of Items', 'Person'] ]
        years = stats.default_years
        tvals = [ [y, 0, 0, 0] for y in years ]
        for idx, obj in enumerate([model.Work, model.Item, model.Person]):
            if obj == model.Person:
                datecol = obj.birth_date_ordered
            else:
                datecol = obj.date_ordered
            y, cumul = stats.by_year(obj.query, datecol)
            perperiod = stats.cumulative_to_per_period(cumul)
            for idx2, v in enumerate(perperiod):
                tvals[idx2][idx+1] = v
        c.by_year_table += tvals
        return render('stats/index')
        

