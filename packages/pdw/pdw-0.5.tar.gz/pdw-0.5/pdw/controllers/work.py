from pdw.lib.base import *

import pdw.name
import pdw.model.frbr

class WorkController(BaseController):
    def index(self):
        c.total = model.Work.query.count()
        return render('work/index')
    
    def read(self, id):
        # Try id as uuid
        work = model.Work.query.get(id)
        if work is None:
            # Try id as readable_id
            works = pdw.model.frbr.get_works_matching_readable_id(id)      
            if len(works) == 1:
                work = works[0]
                #TODO: disambiguation page for multiple results
            else:
                abort(404)
        c.work = work
        return render('work/read')

    def list(self, id=None):
        if id is None: id = 0
        else: id = int(id)
        limit = 50
        offset = id * limit
        c.items = model.Work.query.limit(limit).offset(offset).all()
        return render('work/list')

    def search(self, id=None):
        q = request.params.get('q', '')
        c.q = q
        if q:
            c.had_query = True
            query = model.Work.query.filter(
                    model.Work.title.ilike('%' + q.strip() + '%')
                    )
            c.total = query.count()
            c.results = query.limit(50).all()
        return render('work/search')

