from pdw.lib.base import *

import pdw.name
import pdw.model.frbr

class ItemController(BaseController):
    def index(self):
        c.total = model.Item.query.count()
        return render('item/index')

    def read(self, id):
        # Try id as uuid
        item = model.Item.query.get(id)
        if item is None:
            # Try id as readable_id
            items = pdw.model.frbr.get_items_matching_readable_id(id)      
            if len(items) == 1:
                item = items[0]
                #TODO: disambiguation page for multiple results
            else:
                abort(404)
        c.item = item
        return render('item/read')

    def list(self, id=None):
        if id is None: id = 0
        else: id = int(id)
        limit = 50
        offset = id * limit
        c.items = model.Item.query.limit(limit).offset(offset).all()
        return render('item/list')

    def search(self, id=None):
        q = request.params.get('q', '')
        c.q = q
        if q:
            c.had_query = True
            query = model.Item.query.filter(
                    model.Item.title.ilike('%' + q.strip() + '%')
                    )
            c.total = query.count()
            c.results = query.limit(50).all()
        return render('item/search')

