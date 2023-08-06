from pdw.lib.base import *

class HomeController(BaseController):
    def index(self):
        c.person_total = model.Person.query.count()
        c.work_total = model.Work.query.count()
        c.item_total = model.Item.query.count()
        return render('home')

    def about(self):
        return render('about')
