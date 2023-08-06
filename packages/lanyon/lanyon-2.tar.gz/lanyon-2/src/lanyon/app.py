from codecs import open
from collections import defaultdict
from datetime import datetime
import logging
from optparse import OptionParser
from os import walk, makedirs, error, getcwd
from os.path import splitext, join, dirname, split, abspath, getctime, isdir,\
                    basename

from lanyon import __version__, parser
from lanyon.utils import relpath, copy_file
from lanyon.template import Jinja2Template


class Site(object):

    def __init__(self, project_dir, settings):
        self.project_dir = project_dir
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
        for input_dir in input_data:
            articles, media  = input_data[input_dir]

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
                headers['url'] = relpath(output_path, self.settings['output_dir'])

                if headers['status'] != 'draft' and\
                   headers['date'] <= datetime.today():
                    self.articles.append(dict(headers=headers,
                                              body=parsed[1],
                                              input_path=path,
                                              output_path=output_path,
                                              media=media))

    def _copy_media(self):
        # media that isn't associated with articles
        for medium in self.media:
            dst = join(self.settings['output_dir'],
                       relpath(medium, self.settings['input_dir']))
            copy_file(medium, dst)
        # media that is associated with articles
        for article in self.articles:
            for medium in article['media']:
                dst = join(self.settings['output_dir'],
                           dirname(article['headers']['url']),
                           relpath(medium, dirname(article['input_path'])))
                copy_file(medium, dst)

    def _read_input(self):
        """
        Walks through the input dir and separates files into article
        and media files. Files and directories starting with a dot will
        be ignored.
        """
        data = defaultdict(lambda:([], []))

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
                # dir has media file(s) but no articles. check if one of the parent 
                # dirs has an article and associate the media with it
                parent_dir = dirname(root)
                has_parent = False
                while parent_dir != self.settings['input_dir']:
                    if parent_dir in data:
                        data[parent_dir][1].extend(media)
                        has_parent = True
                    parent_dir = dirname(parent_dir)
                # if no parent dir could be found, associate the files with the
                # root of the input dir
                if not has_parent:
                    data[self.settings['input_dir']][1].extend(media)
        return data

    def _is_public(self, article):
        if article['headers']['status'] != 'hidden':
            return True
        return False

    def _sort_articles(self):
        self.articles.sort(key=lambda x: x['headers']['date'], reverse=True)

    def _write(self):
        public_articles = filter(self._is_public, self.articles)
        template_cls = Jinja2Template(self.settings)
        for article in self.articles:
            try:
                makedirs(dirname(article['output_path']))
            except error, e:
                pass
            relpath_root = relpath(self.settings['output_dir'],
                                   dirname(article['output_path']))
            if article['headers']['template'] == 'self':
                render_func = template_cls.render_string
                template = article['body']
            else:
                render_func = template_cls.render
                template = article['headers']['template']
            rendered = render_func(template,
                                   body=article['body'],
                                   headers=article['headers'],
                                   articles=public_articles,
                                   RELPATH_ROOT=relpath_root,
                                   BUILD_TIME=self.build_time)
            fout = open(article['output_path'], 'w', 'utf-8')
            fout.write(rendered)
            fout.close()

    def run(self):
        input_data = self._read_input()
        self._parse(input_data)
        self._sort_articles()
        self._write()
        self._copy_media()

def main():
    parser = OptionParser(usage="%prog [project_dir]",
                                   version="%prog " + __version__)
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()

    LOGGING_LEVELS = {'critical': logging.CRITICAL,
                      'error': logging.ERROR,
                      'warning': logging.WARNING,
                      'info': logging.INFO,
                      'debug': logging.DEBUG}
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.NOTSET)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    try:
        project_dir = abspath(args[0])
    except IndexError:
        project_dir = abspath(getcwd())
    logging.debug('project dir is "%s"' % project_dir)

    # todo: don't pass project_dir to class, use settings.project_dir
    settings = {'project_dir': project_dir,
                'input_dir': join(project_dir, 'input'),
                'output_dir': join(project_dir, 'output')}
    site = Site(project_dir, settings)
    site.run()

if __name__ == '__main__':
    main()

