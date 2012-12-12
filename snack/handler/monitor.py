
from snack import utils
from snack.handler import base

class Instance(base.BaseHandler):
    def get(self):
        self.render('monitor/instance.html')