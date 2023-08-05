from paste.httpexceptions import HTTPNotFound

from datetime import datetime
import calendar

entries_per_page = 10

class WSGIApplication(object):
    def __init__(self, store):
        self.store = store
    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '').split('/')[1:]
        if len(path_info) == 0:
            path_info.append('index')
        if path_info[-1] == '':
            path_info[-1] = 'index'
        if path_info[-1] != 'index' and path_info[-1] != 'index.atom':
            path_info.append('index')

        if len(path_info) == 1:
            return self.index(environ, start_response)
        elif len(path_info) == 2:
            if path_info[0].isdigit():
                year = int(path_info[0])
                return self.year(environ, start_response, year)
            else:
                return self.not_found(environ, start_response)
        elif len(path_info) == 3:
            if path_info[0] == 'page':
                page = path_info[1]
                if page.isdigit():
                    return self.page(environ, start_response, int(page))
                else:
                    return self.not_found(environ, start_response)
            elif path_info[0].isdigit() and path_info[1].isdigit():
                year = int(path_info[0])
                month = int(path_info[1])
                return self.month(environ, start_response, year, month)
            else:
                return self.not_found(environ, start_response)
        elif len(path_info) == 4:
            if path_info[0].isdigit() and path_info[1].isdigit() and path_info[2].isdigit():
                year = int(path_info[0])
                month = int(path_info[1])
                day = int(path_info[1])
                return self.day(environ, start_response, year, month, day)
            else:
                return self.not_found(environ, start_response)
        else:
            return self.not_found(environ, start_response)

    def return_entries(self, environ, start_response, entries):
        start_response('200 OK', [('Content-type', 'application/atom+xml')])
        is_atom_request = environ.get('PATH_INFO', '').endswith('index.atom')
        environ['brightcontent.render'] = not is_atom_request
        feed = self.store.assemble_feed(entries)
        return [feed]

    def day(self, environ, start_response, year, month, day):
        lower_date = datetime(year, month, day, 0, 0, 0)
        upper_date = datetime(year, month, day, 23, 59, 59)
        entries = self.store.get_entries(lower_date=lower_date,
                upper_date=upper_date)
        return self.return_entries(environ, start_response, entries)

    def month(self, environ, start_response, year, month):
        lower_date = datetime(year, month, 1)
        upper_date = datetime(year, month, calendar.monthrange(year, month)[1])
        entries = self.store.get_entries(lower_date=lower_date,
                upper_date=upper_date)
        return self.return_entries(environ, start_response, entries)

    def year(self, environ, start_response, year):
        lower_date = datetime(year, 1, 1)
        upper_date = datetime(year, 12, 31)
        entries = self.store.get_entries(lower_date=lower_date,
                upper_date=upper_date)
        return self.return_entries(environ, start_response, entries)

    def page(self, environ, start_response, page = 1):
        offset = (page-1) * entries_per_page
        limit = entries_per_page
        entries = self.store.get_entries(offset=offset, limit=limit)
        return self.return_entries(environ, start_response, entries)

    def index(self, environ, start_response):
        return self.page(environ, start_response, 1)

    def not_found(self, environ, start_response):
        return HTTPNotFound()(environ, start_response)
