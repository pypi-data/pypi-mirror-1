from paste.script import templates
vars = [
        templates.var('version', 'Version (like 0.1)'),
        templates.var('description', 'One-line description of the package'),
        templates.var('long_description', 'Multi-line description (in reST)'),
        templates.var('keywords', 'Space-separated keywords/tags'),
        templates.var('author', 'Author name'),
        templates.var('author_email', 'Author email'),
        templates.var('url', 'URL of homepage'),
        templates.var('license_name', 'License name'),
        #templates.var('zip_safe', 'True/False: if the package can be distributed as a .zip file',
            #default=False),
    ]

class FrameworkTemplate(templates.Template):

    egg_plugins = ['datahub']
    summary = 'DataHub is a tool to help you datamine(crawl, parse, and load) any data.'
    required_templates = ['basic_package']
    _template_dir = 'template'
    use_cheetah = True
    vars=vars

    from paste.script import command
    def pre(self, command, output_dir, vars):
        #Add dataurl to a vars lis
        #vars['dataurl']=[]
        #while 1:
        #    url=command.challenge('Please Enter a URL of a Data Source:','done',True)
        #    if url=='done':
        #        break
        #    vars['dataurl'].append(url)
        pass
    def post(self, command, output_dir, vars):
        """This function creates template files for conversion based on the inputed dataurl"""
        #import os
        #from Cheetah.Template import Template
        #if len(vars['dataurl'])<1:
        #    raise ProgrammingError, 'No URL to work with.'
        #for filename in vars['dataurl']:
            #Loop through Filenames
        #    if os.path.splitext(filename)[1]=='.txt':
                #If one of the url ends with .txt create based on this template.
                #Model file
        #        source_filename = os.path.join(os.path.dirname(__file__), '_tmpl/convert/textfiles.py_tmpl')
        #        self.addfile(filenameurl=filename,source_filename=source_filename,command=command,vars=vars)
        #    elif os.path.splitext(filename)[1]=='.csv':
                #If one of the url ends with .txt create based on this template.
        #        source_filename = os.path.join(os.path.dirname(__file__), '_tmpl/convert/csvfiles.py_tmpl')
        #        self.addfile(filenameurl=filename,source_filename=source_filename,command=command,vars=vars)
        pass
    def getfilename(self,filenameurl=None):
        """This functions gets a full url of the filename, and returns just actual filename"""
        if not filenameurl:
            print 'no fileurl to parse'
            return None
        import urlparse
        import os
        #Input: filename
        if filenameurl[:7]=='http://' or filenameurl[:8]=='https://':
            #For url that start with http
            (scheme,netloc,path,parameters,query,fragment)=urlparse.urlparse(filenameurl)
            (subpath,actual_filename)=os.path.split(path)
            #Create Files
        else:
            #For url that doesn't start with http. These get parsed differently by urlparse
            actual_filename=os.path.split(urlparse.urlparse(filenameurl)[2])[1]
            #output: actual_filename
        return actual_filename
    def addfile(self,filenameurl=None,source_file=None,command=None,vars=None):
        """This function creates files in convert,model"""
        if not filenameurl and source_filename:
            print 'no files to create'
            return None
        import os
        actual_filename=self.getfilename(filenameurl=filename) 
        from Cheetah.Template import Template
        content = Template(file=source_filename, searchList=[vars])

        command.ensure_file(os.path.join(vars['package'],vars['package'], 'convert',actual_filename+'.py'), str(content))
        command.ensure_file(os.path.join(vars['package'],vars['package'], 'model',actual_filename+'.py'), str(content))
        return True


