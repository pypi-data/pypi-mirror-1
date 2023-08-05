
class MultiProjectIndex(object):
    '''
    This class should be used inside the trac mod_python 
    handler 'ModPythonHandler.py', specifically, in the
    'send_project_index()' function.

    For example, this file:
        /usr/local/lib/python2.3/site-packages/trac/ModPythonHandler.py

    It should be used in the following manner:

    def send_project_index(req, mpr, dir):
        from adytum.plugins.trac import MultiProjectIndex

        text = MultiProjectIndex()
        text.setTitle('Available Projects')
        text.setBaseURL(mpr.idx_location)
        text.setDirs(dir)

        req.content_type = text.getContentType()
        req.write(text.render())

    '''
    def __init__(self, content_type='text/html'):
        self.content_type = content_type
        self.location = ''
        self.dirs = ''
        self.title = ''
        self.header_file = ''
        self.footer_file = ''
        self.base_url = ''
        
    def setTitle(self, title):
        self.title = title

    def setLocation(self, location):
        self.location = location

    def setBaseURL(self, url):
        self.base_url = url

    def setDirs(self, dir):
        import os
        dirs = [ (x.lower(), x) for x in os.listdir(dir) ]
        dirs.sort()
        self.dirs = [ x[1] for x in dirs ]
        self.base_dir = dir
        default_header = 'header.tmpl'
        default_footer = 'footer.tmpl'
        self.header_file = '%s/%s' % (dir, default_header)
        self.footer_file = '%s/%s' % (dir, default_footer)        

    def getContentType(self):
        return self.content_type

    def getHeader(self):
        '''
        '''
        text = file(self.header_file, 'r').read()
        return text.replace('%%TITLE%%', self.title)

    def getProjectListing(self):
        '''
        We do some strange, custom stuff here in order to get the display
        the way we want it.

            * Internal projects are marked with zi__ProjectName
            * Customer/Partner projects are marked with zp__ProjectName
        '''
        import os
        from ConfigParser import ConfigParser

        cfg = ConfigParser()
        cat_heading = '<h3>%s</h3>'                 # takes the project grouping as a parameter
        heading = '<ul>'
        link = '<li><a href="%s">%s</a> - %s</li>'  # takes the mpr.idx_location/location as the URL
                                                    # and project as the display link, then the desc
        footing = '</ul>'

        listing_data = []
        for project in self.dirs:
            proj_dir = os.path.join(self.base_dir, project)
            #output += '(debug) proj_dir: %s<br/>' % proj_dir
            proj_conf = os.path.join(proj_dir, 'conf/trac.ini')
            #output += '(debug) proj_conf: %s<br/>' % proj_conf
            if os.path.isfile(proj_conf):
                cfg.read(proj_conf)
                url = '%s/%s' % (self.base_url, project)
                hidden_name = cfg.get('project', 'name')
                if hidden_name.startswith('zi__'):
                    cat = 'Internal'
                    name = hidden_name.replace('zi__', '')
                elif hidden_name.startswith('zp__'):
                    cat = 'Customers/Partners'
                    name = hidden_name.replace('zp__', '')
                elif hidden_name.startswith('zd__'):
                    cat = 'Deprecated'
                    name = hidden_name.replace('zd__', '')
                elif hidden_name.startswith('zz__'):
                    cat = 'Miscellany'
                    name = hidden_name.replace('zz__', '')
                else:
                    cat = 'Open Source'
                    name = hidden_name
                descr = cfg.get('project', 'descr')
                listing_data.append((hidden_name, cat, name, url, descr))
        listing_data.sort()
        output = heading
        cat_last = None
        for hidden_name, cat, name, url, descr in listing_data:
            if cat != cat_last:
                output += cat_heading % cat
            output += link % (url, name, descr)
            cat_last = cat
        output += footing
        return output

    def getFooter(self):
        '''
        '''
        return file(self.footer_file, 'r').read()

    def render(self):
        '''
        '''
        output = self.getHeader()
        output += self.getProjectListing()
        output += self.getFooter()
        return output
