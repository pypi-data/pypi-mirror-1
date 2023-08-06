import logging

from divimon.lib.base import *
import os
from sqlalchemy.exceptions import IntegrityError

log = logging.getLogger(__name__)


class UploadController(BaseController):
    permanent_store = '/tmp/divimon-upload/'
    permanent_filename = os.path.join(permanent_store, 'item.csv')

    def _save(self):
        import csv
        c.columns = request.params.dict_of_lists()['column']
        page = ''
        page += '<table>'
        page += '<thead>'
        for col in c.columns:
            page += '<th>%s</th>' % col
        page += '<th>%s</th>' % ''
        page += '</thead>'
        page += '<tbody>'
        for row in csv.reader(open(self.permanent_filename)):
            page += self._save_row(row)
        page += '</tbody>'
        page += '</table>'
        return page

    def _save_row(self, row):
        #print 'Saving %s' % row
        s_entry = ''
        kw = {}
        for cnt in range(0, len(c.columns)):
            s_entry += '<td>%s</td>\n' % (row[cnt])
            #print c.columns[cnt], row[cnt]
            kw[str(c.columns[cnt])] = unicode(row[cnt])
        status = self._save_entry(**kw)
        return '<tr>%s<th>%s</th></tr>' % (s_entry, status)

    def _upload_csv(self):
        import csv
        rows = []
        for row in csv.reader(open(self.permanent_filename)):
            rows.append(row)
        c.rows = rows
        c.columns = self.columns
        return render('/upload_confirm.mako')

    def save(self):
        page = self._save()
        return page

    def upload(self):
        import shutil
        try:
            os.mkdir(self.permanent_store)
        except OSError:
            pass
        myfile = request.POST['file']
        #self.permanent_filename = os.path.join(self.permanent_store,
        #    myfile.filename.lstrip(os.sep))
        permanent_file = open(self.permanent_filename, 'w')
        shutil.copyfileobj(myfile.file, permanent_file)
        #myfile.file.close()
        permanent_file.close()
        return self._upload_csv()
        return 'Successfully uploaded: %s, content: %s' % \
            (myfile.filename, myfile.value)

    def index(self):
        c.columns = self.columns
        return render('/upload.mako')


