import yaml
import markdown
import bs4
import re
import importlib
import os
import requests
import tempfile

from urllib.parse import urlparse
from PIL import Image

from .utils import *

MD_EXT = ['nl2br', 'toc', 'footnotes', 'meta', 'fenced_code']
MD_EXT_CONF = {
    'footnotes': {
        'UNIQUE_IDS': True
    }
}

class Renderer():

    def __init__(self, engine, path, **page_context):
        """
        Renderer constructor.

        **Parameters**

        engine: Engine instance
        path: path to template file
        **page_context: keyword arguments to include in the excecution context for embed python code blocks
        """

        self.engine = engine
        self.path = path

        self.markdown = markdown.Markdown(output_format='html5', extensions=MD_EXT, extension_configs=MD_EXT_CONF)

        self.exec_context = deep_merge(
            self.engine.exec_context,
            page_context,
            {
                'toc': '',
                'include': lambda *a, **k: self.include(*a, **k),
                'get': lambda *a, **k: self.get(*a, **k),
                'image_cache': lambda *a, **k: self.image_cache(*a, **k),
            }
        )
        self.globals = {}
        self.locals = {}

        self.exec_context = deep_merge(self.exec_context, {
        }, update=True)

        self.prerender()



    def render(self, prettify=False):
        """
        Generate html document from source template.
        """

        html = self.include(self.path, **self.exec_context)

        if prettify:
            dom = bs4.BeautifulSoup(html, 'html.parser')
            html = str(dom.prettify())

        return html

    def prerender(self):
        """
        Prerender page to compute table of content, meta informations...
        """
        html = self.render()


        """
        Generate table of content from pre-rendered html.
        Takes the first encountered header (starting with h2) as base level.
        """
        toc = ''
        dom = bs4.BeautifulSoup(html, 'html.parser')
        headers = dom.find_all(re.compile('^h[2-6]$'))
        if headers:

            toc += '<ul>'
            length = len(headers)
            sublevel_opened = 1
            for i in range(length):

                h = headers[i]

                link = '<a href="#%s">%s</a>'  % (h.attrs.get('id'), h.text)
                level = int(h.name[1])

                next = level - 1
                if i < length - 1:
                    next = int(headers[i+1].name[1])

                if next > level:
                    toc += '<li>%s<ul>' % link
                    sublevel_opened += 1
                elif next < level:
                    toc += '<li>%s</li></ul>' % link
                    sublevel_opened -= 1
                    if i < length - 1:
                        toc += '</li>'
                else:
                    toc += '<li>%s</li>' % link

            toc += '</ul>' * sublevel_opened

        """
        Extract meta from markdown headers
        """
        meta = {}
        for k in self.markdown.Meta:
            meta[k] = '\n'.join(self.markdown.Meta[k])

        if 'template' in meta:
            self.path = meta['template']

        """
        Insert toc and meta in exec context for final render
        """
        self.exec_context = deep_merge(self.exec_context, {
            'meta': meta,
            'toc': toc
        }, update=True)

    def resolve_code_blocks(self, content_string, **context):
        """
        Search for python code block patterns and replace them with their result.

        {%%
        # multiline python script
        # stdout output will be captured
        %%}

        {%
        # singleline python script, returned value will be captured
        %}

        **Parameters**

        content_string: string
        **context: keyword arguments to include in the excecution context for embed python code blocks

        **Returns**

        A string
        """
        self.globals = deep_merge(self.exec_context, context)
        locals = deep_merge(self.locals)

        if 'functions.py' in self.engine.sources:
            exec(self.engine.sources['functions.py' ], self.globals, None)

        def exec_repl(m):

            def _print(*args):
                _print._output += '\n'.join([str(a) for a in args]) + '\n'
            _print._output = ''

            command = m.group(1)
            exec(command.strip(), deep_merge(self.globals, {'print': _print}), locals)
            return _print._output

        try:
            content_string = re.sub(r'{%%(.*?)%%}\n?', exec_repl, content_string, flags=re.DOTALL)
        except Exception as e:
            raise e
            return 'ERROR:' + str(e)

        def eval_repl(m):
            command = m.group(1)
            content = eval(command.strip(), self.globals, locals)
            content = str(content)

            return content

        try:
            content_string = re.sub(r'{%(.*?)%}', eval_repl, content_string, flags=re.DOTALL)
        except Exception as e:
            raise e
            return 'ERROR:' + str(e)

        # purge locals to avoid variable leak
        self.locals = {}

        return content_string

    def include(self, path, **context):
        """
        Compile resource and return it.

        **Parameters**

        path: path to resource
        **context: keyword arguments to include in the excecution context for embed python code blocks

        **Returns**

        A dict if requested resource is a YAML file, string otherwise.
        """
        if path == None:
            content = fallback_template
        elif path not in self.engine.sources:
            return 'ERROR: %s not found' % path
        else:
            content = self.engine.sources[path]

        content = self.resolve_code_blocks(content, **context)

        if path != None and '.yml' in path:
            content = yaml.safe_load(content)
        if path == None or '.md' in path:
            content = self.markdown.convert(content)
            # reset parser to prevent duplicated footnotes
            # while keeping metadatas...
            meta = self.markdown.Meta
            self.markdown.reset()
            self.markdown.Meta = meta

        return content

    def get(self, name, default=''):
        """
        Get variable bynamefrom global context with a fallback default value

        **Parameters**

        name: variable name
        default: fallback value if variable is not defined in execution context

        **Returns**

        Variable or fallback value.
        """
        return self.globals[name] if name in self.globals else default


    def image_cache(self, path, resize=None):

        distant_src = 'http://' in path or 'https://' in path

        if not distant_src and not path in self.engine.paths:
            return 'ERROR: %s not found' % path

        if resize == None:
            resize = 200
        width = resize

        cache_path = self.engine.cache_path + '/'

        if distant_src:
            url = urlparse(path)
            cache_path += url.hostname + '-'
            cache_path += url.path.rpartition('/')[2]
        else:
            cache_path += path.partition('.')[0].replace('/', '_')

        gif = False
        if path.rpartition('.')[-1] == 'gif':
            cache_path += '.gif'
            gif = True
        else:
            cache_path += '-R'
            cache_path += 'auto' if width == None else str(resize)
            cache_path += '.jpg'

        if not os.path.exists(cache_path):

            if distant_src:
                print('Downloading & caching distant resource: %s' % path)
                tmp = tempfile.TemporaryFile()
                req = requests.get(path, allow_redirects=True)
                tmp.write(req.content)
                if gif:
                    os.system('cp %s %s' % (tmp.path, cache_path))
                else:
                    src_img = Image.open(tmp)
                    src_img.load()
                tmp.close()
            else:
                print('Caching local resource: %s' % path)
                if gif:
                    os.system('cp %s %s' % (self.engine.paths[path], cache_path))
                else:
                    src_img = Image.open(self.engine.paths[path])

            if not gif:
                aspect_ratio = src_img.height / src_img.width
                height = int(resize * aspect_ratio)

                resized_image = src_img.convert('RGB')
                resized_image = resized_image.resize((resize, height), Image.ANTIALIAS)

                resized_image.save(cache_path, optimize=True,quality=70)

        return_path = cache_path.replace(self.engine.build_path, '')
        if return_path[0] == '/':
            return_path = return_path[1:]

        return return_path
