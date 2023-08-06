import logging
import os.path
import magic
from datetime import datetime
import tempfile
from restish import resource, templating, http
import formish
from formish import fileresource

from pprint import pformat

from testish.lib import forms as form_defs
from testish.lib import extract_function

log = logging.getLogger(__name__)

try:
    import markdown
    def _format(v):
        v = '\n'.join([l[4:] for l in v.split('\n')])
        return markdown.markdown(v)
except ImportError:
    def _format(v):
        v = '\n'.join([l[4:] for l in v.split('\n')])
        return '<pre>%s</pre>'%v

def get_forms(ids):
    out = []
    for f in ids:
        form_attr = 'form_%s'%f
        form_def = getattr(form_defs, form_attr)
        out.append( {'name': f,
        'title': formish.util.title_from_name(f),
        'description': _format(form_def.func_doc),
        'summary': form_def.func_doc.strip().split('\n')[0]})
    return out



class FileAccessor(object):
    """
    A skeleton class that should be implemented so that the files resource can
    build caches, etc
    """

    def __init__(self):
        self.prefix = 'store-%s'%tempfile.gettempprefix()
        self.tempdir = tempfile.gettempdir()


    def get_mimetype(self, filename):
        """
        Get the mime type of the file with this id
        """
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename.split('-')[-1])
        return magic.from_file(actualfilename, mime=True)


    def get_mtime(self, filename):
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename.split('-')[-1])
        if os.path.exists(actualfilename):
            return datetime.fromtimestamp( os.path.getmtime(actualfilename) )
        return datetime(1970, 1, 1, 0, 0)


    def get_file(self, filename):
        """
        Get the file object for this id
        """
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename.split('-')[-1])
        return open(actualfilename).read()

    def file_exists(self, filename):
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename.split('-')[-1])
        return os.path.exists(actualfilename)



class Root(resource.Resource):

    @resource.GET()
    @templating.page('root.html')
    def root(self, request):
        return {'get_forms': get_forms}
    
    def resource_child(self, request, segments):
        if segments[0] == 'filehandler':
            return fileresource.FileResource(fileaccessor=FileAccessor()), segments[1:]
        return FormResource(segments[0]), segments[1:]


class FormResource(resource.Resource):

    def __init__(self, id):
        self.id = id
        self.title = formish.util.title_from_name(id)
        self.form_attr = 'form_%s'%id
        try: 
            self.form_getter = getattr(form_defs,self.form_attr)
        except AttributeError:
            raise http.NotFoundError()
        self.description = _format(self.form_getter.func_doc)
    
    @resource.GET()
    def GET(self, request):
        return self.render_form(request)

    @templating.page('form.html')
    def render_form(self, request, form=None, data=None):
        if request.GET.get('show_tests','False') == 'True':
            tests = '<h4>Selenium (Func) Tests</h4>'
            tests += extract_function.extract('functest_%s'%self.id)
            tests += '<h4>Unit Tests</h4>'
            tests += extract_function.extract('unittest_%s'%self.id)
            tests += '<a href="?show_tests=False">Click here to hide tests</a>'
        else:
            tests = '<a href="?show_tests=True">Click here to see tests</a>'
        if form is None:
            form = self.form_getter(request)
            form.renderer = request.environ['restish.templating.renderer']
        return {'title': self.title, 'description': self.description,
                'form': form, 'data': pformat(data),'rawdata': data,
                'template': extract_function.extract_docstring('template_%s'%self.id),
                'template_highlighted': extract_function.extract_docstring_highlighted('template_%s'%self.id),
                'definition': extract_function.extract(self.form_attr).replace('6LcSqgQAAAAAAGn0bfmasP0pGhKgF7ugn72Hi2va','6LcSqgQA......................ugn72Hi2va'),
                'tests': tests}
    
    @resource.POST()
    def POST(self, request):
        form = self.form_getter(request)
        form.renderer = request.environ['restish.templating.renderer']
        try:
            data = form.validate(request)
        except formish.FormError, e:
            return self.render_form(request, form=form)
        else:
            if 'myFileField' in data and data['myFileField'] is not None:
                f = data['myFileField']
                filedata = f.file.read()
                prefix = 'store-%s'%tempfile.gettempprefix()
                tempdir = tempfile.gettempdir()
                actualfilename = '%s/%s%s'% (tempdir, prefix, f.filename.split('-')[-1])
                out = open(actualfilename,'w')
                out.write(filedata)
                out.close()
                form['myFileField'].widget.filehandler.delete_file(f.filename)
                
            return self.render_form(request, form=None, data=data)
