"""Graphical user interface for template designer"""
import os
import turbogears
from turbogears import controllers
from cherrypy import response

class TemplateBrowser(controllers.Controller):
    """Browse Templates.
       Scans the project directories and
       collect your templates in single page.
    """
    __label__ ="Templates Browser"
    __version__ = "1.0"
    __author__ = "Fred Lin"
    __email__ = "gasolin+tg@gmail.com"
    __copyright__ = "Copyright 2007 Fred Lin"
    __license__ = "MIT"

    baseTemplate = 'templatebrowser'
    #languages = None
    icon = "/tg_static/images/widgets.png"
    need_project = True

    def __init__(self,currentProject=None):
        self.currentProject=currentProject
        if not self.currentProject:
            self.currentProject = os.getcwd()

    def project_files(self):
        """
        Walk through the directory, return the template name, path
        """
        p = turbogears.util.get_package_name()
        base_level = len([x for x in p.split(os.sep) if x])
        fl,dct,visibility = [],{},{}

        def collect_files(file_list, dirpath, namelist):
            level = len([x for x in dirpath.split(os.sep) if x]) - base_level
            slot0 = {  # directory info
                      'dir':os.path.dirname(dirpath),
                      'file_name':os.path.basename(dirpath),
                      'path':dirpath,
                      'isdir':True,
                      'level':level
                    }
            slot1 = [] # children directories info
            slot2 = [] # children files info
            slots = (slot0, slot1, slot2)
            dct[dirpath] = slots
            if level:
                dct[os.path.dirname(dirpath)][1].append(slots)
            else:
                file_list.append(slots)
            namelist.sort()
            for name in namelist[:]:
                if name.startswith('.') or name in ['static', 'sqlobject-history']:
                    namelist.remove(name)
                    continue
                p = os.path.join(dirpath, name)
                if os.path.isfile(p) and os.path.splitext(name)[-1] in ['.kid','.tmpl','.html']:
                    slot2.append({
                                   'dir':dirpath,
                                   'file_name':name,
                                   'path':p,
                                   'isdir':os.path.isdir(p),
                                   'level':level+1
                                 })
            # decide if current directory (and ancestors) should be visible
            visibility[dirpath] = bool(slot2)
            if slot2:
                while not visibility.get(os.path.dirname(dirpath), True):
                    dirpath = os.path.dirname(dirpath)
                    visibility[dirpath] = True

        os.path.walk(p, collect_files, fl)
        return [x for x in turbogears.util.flatten_sequence(fl)
                if not x["isdir"] or visibility[x["path"]]]

    def index(self):
        return dict(project_files=self.project_files())
    index = turbogears.expose(template='%s.templater'% baseTemplate)(index)

    def render(self, filename, ContentType):
        """
        render the template to any format
        """
        project_files=self.project_files()
        for file in project_files:
            if file['file_name']==filename:
                response.headerMap['Content-Type']= ContentType
                f=open(self.currentProject+'/'+file['path'],'r')
                #return dict(content = f.read())
                return f.read()

    @turbogears.expose()
    def preview(self, filename):
        """
        Get template name and serve the template as static file
        """
        return self.render(filename, ContentType = 'application/xhtml+xml')

    @turbogears.expose()
    def plain(self, filename):
        """
        Get template name and serve the template as text file
        """
        return self.render(filename, ContentType = 'text/plain')
