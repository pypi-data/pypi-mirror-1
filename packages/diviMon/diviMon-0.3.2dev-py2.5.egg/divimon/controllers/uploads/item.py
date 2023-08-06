import logging

from divimon.lib.base import *

log = logging.getLogger(__name__)

class ItemController(BaseController):
    table = model.Item
    columns = ['name', 'code', 'description', 'unit', 'price', 'qty']
    permanent_store = '/tmp/divimon-item/'

    def _upload_csv(self):
        import csv
        rows = []
        for row in csv.reader(open(self.permanent_filename)):
            rows.append(row)
        return str(rows)

    def simple_upload(self):
        myfile = request.POST['file']
        return 'Successfully uploaded: %s, size: %i\nContents: %s' % \
        (myfile.filename, len(myfile.value), myfile.value)

    def upload(self):
        import os
        import shutil
        try:
            os.mkdir(self.permanent_store)
        except OSError:
            pass
        myfile = request.POST['file']
        self.permanent_filename = os.path.join(self.permanent_store,
            myfile.filename.lstrip(os.sep))
        permanent_file = open(self.permanent_filename, 'w')
        shutil.copyfileobj(myfile.file, permanent_file)
        #myfile.file.close()
        permanent_file.close()
        return self._upload_csv()
        return 'Successfully uploaded: %s, content: %s' % \
            (myfile.filename, myfile.value)

    def index(self):
        return render('/upload.mako')

