import BaseHTTPServer
from codecs import open
from collections import defaultdict, namedtuple
from datetime import datetime
import logging
from optparse import OptionParser
from os import walk, makedirs, getcwd
from os.path import splitext, join, dirname, split, abspath, getctime, isdir,\
                    basename, exists, relpath, isabs
from shutil import rmtree
import sys

from lanyon import __version__, parser
from lanyon.utils import copy_file
from lanyon.template import Jinja2Template
from lanyon.server import LanyonHTTPRequestHandler


class Site(object):

    def __init__(self, settings):
        self.settings = settings
        self.articles = []
        self.media = []
        self.build_time = datetime.today()

    def _get_default_headers(self, path):
        """
        Returns a dictionary with the default headers for an article.

        `title` - titleized version of the filename
        `date` - set to ctime. On unix this is the time of the most recent
                 metadata change; on windows the creation time
        `status` - set to 'live'
        `template` - set to 'default.html'
        """
        name = split(splitext(path)[0])[1]
        title = name.title()
        # todo: check if ctime is successfull
        date = datetime.fromtimestamp(getctime(path))
        return dict(title=title, date=date, status='live',
                    template='default.html')

    def _get_output_path(self, input_path, url, output_ext):
        """
        Returns the absolute output path for an article.

        `input_path` - absolute path of the input file
        `url` - parsed "url" header. This may be None if the article
                hasn't specified such a header.
        `output_ext` - file extension of the output file as specified
                       by the parser.
        """
        if url:
            if isabs(url):
                url = url[1:]
            if not basename(url):
                # url is a directory
                output_path = join(url, 'index.html')
            else:
                # url is a filename
                output_path = url
        else:
            output_file = splitext(input_path)[0] + '.' + output_ext
            output_path = relpath(output_file, self.settings['input_dir'])
        return join(self.settings['output_dir'], output_path)

    def _parse(self, input_data):
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
                parser_inst = parser.get_parser_for_filename(path)(f.read())
                f.close()
                parsed = parser_inst.parse()

                output_ext = parser_inst.output_ext or \
                             splitext(path)[1][1:]
                output_path = self._get_output_path(path,
                                                    parsed[0].get('url'),
                                                    output_ext)

                # replace default headers with headers from the article
                default_headers = self._get_default_headers(path)
                headers = dict(default_headers, **parsed[0])
                headers['url'] = relpath(output_path,
                                         self.settings['output_dir'])

                # special case: remove 'index.html' from url
                head, tail = split(headers['url'])
                if tail == 'index.html':
                    headers['url'] = head + '/'

                if headers['status'] != 'draft' and\
                   headers['date'] <= datetime.today():
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

        for root, dirs, files in walk(self.settings['input_dir']):
            articles = []
            media = []

            # don't visit hidden directories
            for dir in dirs:
                if dir.startswith('.'):
                    dirs.remove(dir)

            # sort files into articles and media
            for file in files:
                if file.startswith('.'):
                    continue
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
        """Sort articles by date"""
        self.articles.sort(key=lambda x: x.headers['date'], reverse=True)

    def _delete_output_dir(self):
        """Deletes the output directory"""
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
                                   BUILD_TIME=self.build_time)
            logging.debug("writing %s to %s", article.input_path,
                                              article.output_path)
            fout = open(article.output_path, 'w', 'utf-8')
            fout.write(rendered)
            fout.close()

    def run(self):
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
        print("OK (%s articles)" % len(self.articles))


def main():
    parser = OptionParser(usage="%prog [project_dir]",
                                   version="%prog " + __version__)
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    parser.add_option('-p', '--port', help='Webserver port number',
                      default=8000, type='int')
    parser.add_option('-s', '--serve', help='Use local webserver',
                      action="store_true", dest="serve")
    (options, args) = parser.parse_args()

    LOGGING_LEVELS = {'critical': logging.CRITICAL,
                      'error': logging.ERROR,
                      'warning': logging.WARNING,
                      'info': logging.INFO,
                      'debug': logging.DEBUG}
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.INFO)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    try:
        project_dir = abspath(args[0])
    except IndexError:
        project_dir = abspath(getcwd())
    settings = {'project_dir': project_dir,
                'input_dir': join(project_dir, 'input'),
                'output_dir': join(project_dir, 'output'),
                'template_dir': join(project_dir, 'templates')}

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
        httpd.serve_forever()
    if options.serve:
        import autoreload
        autoreload.main(runserver, (), {
            'paths': (settings['input_dir'], settings['template_dir'])})
    else:
        site.run()

if __name__ == '__main__':
    main()
