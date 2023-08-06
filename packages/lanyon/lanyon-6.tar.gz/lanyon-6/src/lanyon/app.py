import BaseHTTPServer
from codecs import open
from collections import defaultdict, namedtuple
from datetime import datetime
from fnmatch import fnmatch
import imp
import logging
from optparse import OptionParser
from os import makedirs, getcwd
from os.path import splitext, join, dirname, split, abspath, getctime, isdir,\
                    basename, exists, relpath, isabs
from shutil import rmtree
from string import Template
import sys
import time

from lanyon import __version__, parser
from lanyon.utils import copy_file, walk_ignore
from lanyon.template import Jinja2Template
from lanyon.server import LanyonHTTPRequestHandler
from lanyon.url import registry


class Site(object):

    def __init__(self, settings):
        self.settings = settings
        self.articles = []
        self.media = []

    def _get_default_headers(self, path):
        """
        Return the default headers for an article.

        `title` - titleized version of the filename
        `date` - set to ctime. On unix this is the time of the most recent
                 metadata change; on windows the creation time
        `status` - set to 'live'
        `template` - set to 'default.html'
        `url` - set to "default" rule
        `slug` - filename or, if the filename is "index", the dirname
               of the parent directory unless its the top level dir.
        """
        root, filename = split(splitext(path)[0])
        if filename == 'index' and root != self.settings['input_dir']:
            slug = basename(root)
        else:
            slug = filename
        title = filename.title()
        try:
            date = datetime.fromtimestamp(getctime(path))
        except OSError:
            # use the current date if the ctime cannot be accessed
            date = datetime.now()
        return dict(title=title, date=date, status='live', slug=slug,
                    template='default.html', url='default')

    def _get_output_path(self, url):
        """
        Return the absolute output path for an article.

        Keyword arguments:
        url -- the parsed "url" header from the article
        """
        if isabs(url):
            # omit starting slash char; if we wouldn't do this, the
            # join() below would return a path that starts from 
            # the root of the filesystem instead of the output_dir.
            url = url[1:]
        if not basename(url):
            # url is a directory -> write to 'index.html'
            output_path = join(url, 'index.html')
        else:
            # url is a filename
            output_path = url
        return join(self.settings['output_dir'], output_path)

    def _load_custom_urls(self):
        """Return custom url patterns."""
        path = join(self.settings['project_dir'], 'urls.py')
        try:
            urls = imp.load_source('urls', path)
        except IOError:
            logging.debug('couldn\'t load urls from "%s"', path)

    def _get_url_func(self, path, url):
        """
        Return the function that generates the url.

        Keyword arguments:
        path -- absolute path to the input file
        url -- url specified in the article's header
        """
        path = relpath(path, self.settings['input_dir'])
        for pattern in reversed(registry):
            rules = registry[pattern]
            if fnmatch(path, pattern):
                if url in rules:
                    return rules[url]
                elif pattern == '*' and url != 'default':
                    # special case: user entered something but it isn't
                    # a url function -> assume its an output path 
                    return lambda **x: url
                elif 'default' in rules:
                    return rules['default']

    def _parse(self, input_data):
        self._load_custom_urls()
        Article = namedtuple('Article',
                             'headers, body, input_path, output_path, media')
        for input_dir in input_data:
            articles, media = input_data[input_dir]

            # special case: media in the root input dir is not
            # associated with any articles
            if input_dir == self.settings['input_dir']:
                self.media = media
                media = []
            for path in articles:
                f = open(path, 'r', encoding='utf8')
                parser_cls = parser.get_parser_for_filename(path)
                parser_inst = parser_cls(self.settings, f.read())
                f.close()

                try:
                    parsed = parser_inst.parse()
                except parser.ParserException as parser_error:
                    logging.error(parser_error)
                    logging.error('skipping article "%s"', path)
                    continue

                output_ext = parser_cls.output_ext or splitext(path)[1][1:]

                # replace default headers with headers from the article
                default_headers = self._get_default_headers(path)
                headers = dict(default_headers, **parsed[0])

                # don't process drafts and future-dated articles
                if headers['status'] == 'draft' or \
                   headers['date'] > datetime.today():
                    continue

                # resolve custom url pattern
                url_func = self._get_url_func(path, headers['url'])
                headers['url'] = url_func(**dict(
                    path=relpath(path, self.settings['input_dir']),
                    extension=output_ext,
                    headers=headers,
                ))
                # variable subst
                substitute_vars = dict(
                    year=headers['date'].year,
                    month=headers['date'].strftime('%m'),
                    day=headers['date'].strftime('%d'),
                    slug=headers['slug'],
                    ext=output_ext,
                )
                headers['url'] = Template(headers['url']).safe_substitute(
                                    substitute_vars)
                output_path = self._get_output_path(headers['url'])
                self.articles.append(Article(headers=headers,
                                             body=parsed[1],
                                             input_path=path,
                                             output_path=output_path,
                                             media=media))
                sys.stdout.write('.')
        sys.stdout.write('\n')

    def _copy_media(self):
        # media that isn't associated with articles
        for medium in self.media:
            dst = join(self.settings['output_dir'],
                       relpath(medium, self.settings['input_dir']))
            copy_file(medium, dst)
        # media that is associated with articles
        for article in self.articles:
            for medium in article.media:
                dst = join(self.settings['output_dir'],
                           dirname(article.output_path),
                           relpath(medium, dirname(article.input_path)))
                copy_file(medium, dst)

    def _read_input(self):
        """
        Walks through the input dir and separates files into article
        and media files. Files and directories starting with a dot will
        be ignored.
        """
        data = defaultdict(lambda: ([], []))

        for root, dirs, files in walk_ignore(self.settings['input_dir']):
            articles = []
            media = []

            # sort files into articles and media
            for file in files:
                path = join(root, file)
                if parser.get_parser_for_filename(path):
                    articles.append(path)
                else:
                    media.append(path)

            if articles:
                data[root] = (articles, media)
            elif media:
                # dir has media file(s) but no articles. check if one of
                # the parent dirs has an article and associate the media
                # with it
                has_parent = False
                if root != self.settings['input_dir']:
                    parent_dir = dirname(root)
                    while parent_dir != self.settings['input_dir']:
                        if parent_dir in data:
                            data[parent_dir][1].extend(media)
                            has_parent = True
                        parent_dir = dirname(parent_dir)
                # if no parent dir could be found, or the file is in the
                # root dir associate the files with the root of the input dir
                if not has_parent:
                    data[self.settings['input_dir']][1].extend(media)
        return data

    def _is_public(self, article):
        """Return True if article is public"""
        if article.headers['status'] != 'hidden':
            return True
        return False

    def _sort_articles(self):
        """Sort articles by date (newest first)"""
        self.articles.sort(key=lambda x: x.headers['date'], reverse=True)

    def _delete_output_dir(self):
        """Delete the output directory"""
        if exists(self.settings['output_dir']):
            rmtree(self.settings['output_dir'])

    def _write(self):
        public_articles = filter(self._is_public, self.articles)
        template_cls = Jinja2Template(self.settings)
        for article in self.articles:
            try:
                makedirs(dirname(article.output_path))
            except OSError:
                pass
            if article.headers['template'] == 'self':
                render_func = template_cls.render_string
                template = article.body
            else:
                render_func = template_cls.render
                template = article.headers['template']
            rendered = render_func(template,
                                   body=article.body,
                                   headers=article.headers,
                                   articles=public_articles,
                                   settings=self.settings)
            logging.debug("writing %s to %s", article.input_path,
                                              article.output_path)
            fout = open(article.output_path, 'w', 'utf-8')
            fout.write(rendered)
            fout.close()

    def run(self):
        start_time = time.time()
        logging.debug("project directory: %s", self.settings['project_dir'])
        logging.debug("reading input files")
        input_data = self._read_input()
        logging.debug("parsing files")
        self._parse(input_data)
        self._sort_articles()
        logging.debug("writing files")
        self._delete_output_dir()
        self._write()
        self._copy_media()
        logging.debug("%s articles written", len(self.articles))
        finish_time = time.time()
        article_count = len(self.articles)
        print("OK (%s %s; %s seconds)" % (
            article_count,
            'article' if article_count == 1 else 'articles',
            round(finish_time - start_time, 2)))

def main():
    # parse options
    parser = OptionParser(usage="%prog [project_dir]",
                                   version="%prog " + __version__)
    parser.add_option('--date-format',
                      help='Date format used in articles (default: %Y-%m-%d)',
                      default='%Y-%m-%d')
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    parser.add_option('-p', '--port',
                      help='Webserver port number (default: 8000)',
                      default=8000, type='int')
    parser.add_option('-o', '--output-dir', help='Output directory',
                      type='string')
    parser.add_option('-s', '--serve', help='Use local webserver',
                      action="store_true", dest="serve")
    parser.add_option('--noreload', help='Do NOT use the autoreloader',
                      action="store_true", dest="noreload")
    (options, args) = parser.parse_args()

    try:
        project_dir = abspath(args[0])
    except IndexError:
        project_dir = abspath(getcwd())
    settings = {'project_dir': project_dir,
                'input_dir': join(project_dir, 'input'),
                'output_dir': join(project_dir, 'output'),
                'template_dir': join(project_dir, 'templates'),
                'build_time': datetime.today(),
                'date_format': options.date_format}
    if options.output_dir:
        settings['output_dir'] = options.output_dir

    # logging
    LOGGING_LEVELS = {'critical': logging.CRITICAL,
                      'error': logging.ERROR,
                      'warning': logging.WARNING,
                      'info': logging.INFO,
                      'debug': logging.DEBUG}
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.INFO)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # check if an input directory exists
    if not exists(settings['input_dir']):
        print('abort: There is no "input" directory at %s' %
              settings['project_dir'])
        sys.exit()

    site = Site(settings)

    def runserver(server_class=BaseHTTPServer.HTTPServer,
                  handler_class=LanyonHTTPRequestHandler,
                  *args, **kwargs):
        site.run()
        handler_class.rootpath = settings['output_dir']
        server_address = ('', options.port)
        httpd = server_class(server_address, handler_class)
        logging.info("serving at port %s", server_address[1])
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)
    if options.serve:
        if options.noreload:
            runserver()
        else:
            import autoreload
            autoreload.main(runserver, (), {
                'paths': (settings['input_dir'], settings['template_dir'])})
    else:
        site.run()

if __name__ == '__main__':
    main()
