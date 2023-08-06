import distutils, os, pkg_resources, urllib2
from setuptools import Command
from distutils.util import convert_path
from distutils import log
from distutils.errors import *

class wikiup(Command):
    """Upload pages to a wiki"""

    description = "upload wiki pages specified in wikiup.cfg"

    user_options = [
        ('config-file=', 'C', "file with page info (default: wikiup.cfg)"),
        ('comment=', 'c', "Revision comment to use (default: none)"),
    ]

    def initialize_options(self):
        self.config_file = self.comment = None
        self.wikis = {}

    def finalize_options(self):
        if self.config_file is None:
            self.config_file = 'wikiup.cfg'

    def run(self):
        wiki_pages = list(self.get_pages())
        if not wiki_pages:
            log.warn("No wiki pages defined -- skipping upload")
        else:
            for wiki, pagename, filename in wiki_pages:
                f = open(convert_path(filename))
                page = f.read()
                f.close()
                plugin = self.get_wiki(wiki)
                log.info("uploading %s to %s::%s", filename, wiki, pagename)
                plugin.upload_page(pagename, page)





    def get_wiki(self, wiki):
        """Return a Wiki object for the named wiki"""
        try:
            return self.wikis[wiki]
        except KeyError:
            pass

        key = 'wikiup-'+wiki
        if key not in self.distribution.command_options:
            raise DistutilsOptionError(
                "No configuration for wiki %r" % (wiki,))

        options = self.distribution.command_options[key]
        if 'type' not in options:
            raise DistutilsOptionError(
                "%r section must include a 'type' setting" % (key,))

        plugin_name = options['type'][1]
        for ep in pkg_resources.iter_entry_points('wikiup.plugins', plugin_name):
            plugin = self.wikis[wiki] = ep.load()(self, wiki, options)
            plugin.login()
            return plugin

        raise DistutilsModuleError(
            "No plugin found to handle wiki %r of type %r (found in %r)"
            % ((wiki,) + options['type'][::-1])
        )














    def get_pages(self):
        """Yield wiki,page,file triples from our config file"""

        if not os.path.exists(self.config_file):
            return  # no pages here           

        for wiki,pages in pkg_resources.split_sections(file(self.config_file)):
            if wiki is None and pages:
                raise DistutilsOptionError(
                    "Unlabelled section in "+self.config_file
                )
            for line in pages:
                if '=' in line:
                    pagename, filename = line.split('=', 1)
                else:
                    pagename = filename = line
                yield wiki, pagename.strip(), filename.strip()
























class Wiki(object):
    """Base class for wikis"""

    required_options = dict(
        url = "Base URL of the Wiki",
    )

    url = None
    
    def __init__(self, command, name, options):
        for cls in type(self).__mro__:
            if issubclass(cls, Wiki):
                for k in cls.required_options:
                    if k not in options and getattr(self, k, None) is None:
                        raise DistutilsOptionError(
                            "Missing option %r for wiki %r: %s" %
                            (k, name, cls.required_options[k])
                        )
        cls = type(self)
        for k in options:
            v = getattr(cls, k, None)
            if v is not None and not isinstance(v, basestring):
                raise DistutilsOptionError(
                    "Unrecognized option %r for wiki %r: %s" %
                    (k, name, options[k])
                )
            setattr(self, k, options[k][1])            

        self.command = command
        self.name = name

    def login(self):
        raise NotImplementedError

    def upload_page(self, pagename, page):
        raise NotImplementedError
        




class OldMoin(Wiki):
    """Old MoinMoin, as used on PEAK DevCenter"""

    uid = None
    page_format = r"#format rst\n%s"

    def login(self):
        from mechanize import Browser
        self.browser = Browser()
        if self.uid:
            log.debug("Logging in to %s wiki", self.name)
            self.browser.open(self.url+'?action=userform&uid='+self.uid)
            
    def upload_page(self, pagename, page):
        url = self.url
        if not url.endswith('/'):
            url+='/'
        url += pagename

        self.browser.open(url+'?action=edit')
        self.browser.select_form(nr=0)        
        page = self.page_format.decode('string_escape') % (page,)

        if self.browser['savetext'].splitlines()==page.splitlines():
            log.info("Page %s is unchanged; not saving", pagename)
            return

        if self.command.comment:
            self.browser['comment'] = self.command.comment

        #self.browser['notify']=[]

        self.browser['savetext'] = page
        self.browser.submit()







def additional_tests():
    import doctest
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
    )



































