from pdw.lib.base import *

import pdw.name
import pdw.model.frbr

class PersonController(BaseController):
    def index(self):
        c.total = model.Person.query.count()
        return render('person/index')

    def read(self, id):
        # Try id as uuid
        artist = model.Person.query.get(id)
        if artist is None:
            # Try id as readable_id
            persons_query = pdw.model.frbr.get_persons_matching_readable_id_query(id)
            num_persons = persons_query.count()
            if num_persons == 1:
                artist = persons_query.first()
            elif num_persons > 1:
                c.extra_title = 'to resolve ambiguous name'
                c.q = persons_query.first().name
                c.had_query = True
                c.total = num_persons
                c.results = persons_query.limit(50).all()
                return render('person/search')
            else:
                abort(404)                
        c.is_pd = 'Not Yet Determined'
        c.artist = artist
        return render('person/read')

    def list(self, id=None):
        if id is None: id = 0
        else: id = int(id)
        limit = 50
        offset = id * limit
        
        c.artists = model.Person.query.limit(limit).offset(offset).all()
        return render('person/list')

    def search(self, id=None):
        q = request.params.get('q', '')
        c.q = q
        if q:
            c.had_query = True
            query = model.Person.query.filter(
                    model.Person.name.ilike('%' + q.strip() + '%')
                    )
            c.total = query.count()
            c.results = query.limit(50).all()
        return render('person/search')

    def edit(self, id):
        # TODO
        artist = model.Person.query.get(id)
        if artist is None:
            abort(404)
        if 'commit' in request.params:
            # save
            # not ok. set error and resend
            # ok
            h.redirect(controller='person', action='read', id=id)
        elif 'preview' in request.params:
            c.preview = ''
        else: # default do nothing 
            pass
        return render('person/edit') 

