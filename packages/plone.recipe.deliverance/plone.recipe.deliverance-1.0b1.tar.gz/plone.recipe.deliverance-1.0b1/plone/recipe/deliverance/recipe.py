import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util

import zc.recipe.egg

import templates

def system(c):
    if os.system(c):
        raise SystemError("Failed", c)

class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        
        options.setdefault('eggs', 'Deliverance\nPasteScript')
        options.setdefault('scripts', 'paster')
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        
        self.libxml2_url = options.get('libxml2-url', 'http://xmlsoft.org/sources/libxml2-2.6.29.tar.gz')
        self.libxslt_url = options.get('libxslt-url', 'http://xmlsoft.org/sources/libxslt-1.1.21.tar.gz')
        
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name
            )

    def install(self):
        options = self.options
        location = options['location']
        
        self.egg.install()
        
        if not os.path.exists(location):
            os.mkdir(location)
        
        here = os.getcwd()
        
        try:
            os.chdir(location)
            
            # Build libxml2 and libxslt, unless buildout.cfg specifically
            # set those to a false value
            
            if self.libxml2_url:
                self.cmmi(self.libxml2_url, '--without-python', location)
            
            if self.libxslt_url:
                self.cmmi(self.libxslt_url, '--without-python --with-libxml-prefix=%s' % location, location)

            # Generate a deliverance environment
            self.deliverance_layout()
            self.generate_wrapper()
        
        finally:
            os.chdir(here)

        return location

    def update(self):
        self.deliverance_layout()
        self.generate_wrapper()

    def cmmi(self, url, extra_options, location):
        
        # Code largely borrowed from zc.recipe.cmmi
        
        _, _, urlpath, _, _, _ = urlparse.urlparse(url)
        tmp = tempfile.mkdtemp('buildout-'+self.name)
        tmp2 = tempfile.mkdtemp('buildout-'+self.name)
        try:
            fname = os.path.join(tmp2, urlpath.split('/')[-1])
            open(fname, 'w').write(urllib2.urlopen(url).read())
            setuptools.archive_util.unpack_archive(fname, tmp)
            
            here = os.getcwd()
            os.chdir(tmp)                                        
            try:
                if not os.path.exists('configure'):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                    else:
                        raise ValueError("Couldn't find configure")
                
                system("./configure --prefix=%s %s" % (location, extra_options))
                system("make")
                system("make install")
                
            finally:
                os.chdir(here)

        finally:
            shutil.rmtree(tmp)
            shutil.rmtree(tmp2)
            
    def deliverance_layout(self, force=False, update_settings=True):
        options = self.options
        directory = self.buildout['buildout']['directory']
        
        layout_directory = os.path.join(directory, self.name)
        if force and os.path.exists(layout_directory):
            shutil.rmtree(layout_directory)
            
        new = False
        
        if not os.path.exists(layout_directory):
            os.mkdir(layout_directory)
            new = True
        
        if not os.path.exists(os.path.join(layout_directory, 'static')):
            os.mkdir(os.path.join(layout_directory, 'static'))
            new = True
        
        if not os.path.exists(os.path.join(layout_directory, 'rules')):
            os.mkdir(os.path.join(layout_directory, 'rules'))
            new = True
            
        if not new and not update_settings:
            return
            
        # Write ini file
        
        ini_path = os.path.join(layout_directory, 'deliverance-proxy.ini')
        if os.path.exists(ini_path):
            os.unlink(ini_path)

        open(ini_path, 'w').write(templates.DELIVERANCE_INI % {
                'location'  : layout_directory,
                'directory' : directory,
                'name'      : self.name,

                'debug' : options.get('debug', 'true'),                
                'host'  : options.get('host', '0.0.0.0'),
                'port'  : options.get('port', '8000'),
                'proxy' : options.get('proxy', 'http://localhost:8080'),
                'theme' : options.get('theme', '/.deliverance/static/theme.html'),
                'rules' : options.get('rules', '/.deliverance/rules/rules.xml'),
                
                'transparent' : options.get('transparent', 'true'),
                'rewrite' : options.get('rewrite', 'true'),
            })
            
        # Make sure we have var and log directories
        if not os.path.exists(os.path.join(directory, 'var')):
            os.mkdir(os.path.join(directory, 'var'))
        if not os.path.exists(os.path.join(directory, 'var', self.name)):
            os.mkdir(os.path.join(directory, 'var', self.name))
            
        if not os.path.exists(os.path.join(directory, 'log')):
            os.mkdir(os.path.join(directory, 'log'))
        if not os.path.exists(os.path.join(directory, 'log', self.name)):
            os.mkdir(os.path.join(directory, 'log', self.name))
            
        # Put boilerplate theme and rules in place if necessary
        if not os.path.exists(os.path.join(layout_directory, 'static', 'theme.html')):
            open(os.path.join(layout_directory, 'static', 'theme.html'), 'w').write(templates.DEFAULT_THEME)
            
        if not os.path.exists(os.path.join(layout_directory, 'rules', 'rules.xml')):
            open(os.path.join(layout_directory, 'rules', 'rules.xml'), 'w').write(templates.DEFAULT_RULES)
            
            if not os.path.exists(os.path.join(layout_directory, 'rules', 'standardrules.xml')):
                open(os.path.join(layout_directory, 'rules', 'standardrules.xml'), 'w').write(templates.STANDARD_RULES)
    
    def generate_wrapper(self):
        
        options = self.options
        
        directory = self.buildout['buildout']['directory']
        shell = options.get('shell', '/bin/bash')
         
        bin_dir = os.path.join(directory, 'bin')
        bin_path = os.path.join(bin_dir, self.name)
        lib_path = os.path.join(options['location'], 'lib')
        ini_path = os.path.join(directory, self.name, 'deliverance-proxy.ini')
        
        if os.path.exists(bin_path):
            os.unlink(bin_path)
        
        bin_file = open(bin_path, 'w')
        
        print >> bin_file, "#!%s" % shell
        print >> bin_file, "export LD_LIBRARY_PATH=%s" % lib_path
        print >> bin_file, "export DYLD_LIBRARY_PATH=%s" % lib_path
        print >> bin_file, "%s serve %s $@" % (os.path.join(bin_dir, 'paster'), ini_path)
        
        bin_file.close()
        os.chmod(bin_path, 755) # XXX: This doesn't set permissions the way I think it should :)