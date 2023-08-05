from maharishi.lib.base import *

class HelloController(BaseController):
    def index(self):
        return Response('hello world')
    def serverinfo(self):
	session['name'] = 'George'
	session.save()
	return render_response('/serverinfo.myt')
