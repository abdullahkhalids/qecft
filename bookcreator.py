#!/home/abdullah/Apps/miniconda3/bin/python
"""Creates a book out of a collection of jupyter notebooks."""

import shutil
import os
import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor, RegexRemovePreprocessor
from traitlets.config import Config
from jinja2 import Environment, FileSystemLoader

SITENAME = 'A Methods Focused Guide to Quantum Error Correction and Fault-Tolerant Quantum Computation'
#SITEURL = 'http://localhost:8000'
#SITEURL = 'http://localhost:8000/qecft'
SITEURL = 'https://abdullahkhalid.com/qecft'
REPOSITORY = 'https://github.com/abdullahkhalids/qecft'
BUILDDIR = 'build'
SOURCEDIR = 'chapters'
FIRST_PAGE_TITLE = 'About this book'

jinja2_config = {
    'comment_start_string': '<!--',
    'comment_end_string': '-->',
    'trim_blocks': True,
    'lstrip_blocks': True,
    'keep_trailing_newline': True,
    'extensions': []
}

c = Config()
c.TagRemovePreprocessor.remove_cell_tags = ("remove-cell",)
c.TagRemovePreprocessor.enabled = True
c.RegexRemovePreprocessor.patterns = r'\s*\Z'
c.RegexRemovePreprocessor.enabled = True
c.HTMLExporter.template_name = "jupyter-html-template"

html_exporter = HTMLExporter(config=c)
html_exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)
html_exporter.register_preprocessor(RegexRemovePreprocessor(config=c), True)
html_exporter.anchor_link_text = '#'

file_loader = FileSystemLoader('website-jinja-template')
env = Environment(loader=file_loader, **jinja2_config)
template = env.get_template('page.html')


def convert_section_to_html(section):
    """Convert ipynb to md."""
    j2_vars = {
        'SITENAME': SITENAME,
        'SITEURL': SITEURL,
        'REPOSITORY': REPOSITORY,
        'page': section,
        'toc': toc_structure
    }

    os.makedirs(section.target_dir)
    with open(section.target_file, 'w') as f:
        f.write(template.render(**j2_vars))


def process_static_resources():
    """Copy static resources into the build folder."""
    shutil.copytree('static',
                    os.path.join(BUILDDIR, 'static'))
    shutil.copytree('images',
                    os.path.join(BUILDDIR, 'images'))


def create_toc_structure():
    """Determine the structure of the book."""

    class Section:
        def __init__(self, ch_dir, sec_filebasename, ch_index, sec_index):
            self.source_dir = os.path.join(SOURCEDIR, ch_dir)
            self.source = os.path.join(self.source_dir,
                                       sec_filebasename + '.ipynb')

            self.target_dir = os.path.join(BUILDDIR, ch_dir, sec_filebasename)
            self.target_file = os.path.join(self.target_dir, 'index.html')
            self.index = sec_index
            self.ch_index = ch_index

            self.url = os.path.join(ch_dir,
                                    sec_filebasename)

            notebook_node = nbformat.read(self.source, 4)

            rawhtml = html_exporter.from_notebook_node(notebook_node)[0]

            # the title is from the first cell
            title = notebook_node.cells[0].source[2:]

            self.caption = title
            self.title = title
            self.content = rawhtml

            self.prevpage = None
            self.nextpage = None

        def __repr__(self):
            return self.source

        def __eq__(self, other):
            return self.source == other.source

    class Chapter:
        def __init__(self, ch_dir, caption, index):
            self.caption = caption
            self.source_dir = os.path.join(SOURCEDIR, ch_dir)
            self.target_dir = os.path.join(BUILDDIR, ch_dir)
            self.index = index
            self.sections = []

        def __iter__(self):
            return self.sections.__iter__()

        def __len__(self):
            return self.sections.__len__()

    class Toc:
        def __init__(self):
            self.chapters = []
            self.sections = []

        def __iter__(self):
            return self.chapters.__iter__()

        def add_section(self, section, ch_index=-1):
            self.chapters[ch_index].sections.append(section)
            self.sections.append(section)

    toc_structure = Toc()
    # read the order file to determine the order of the chapters
    chapter_order_file = os.path.join(SOURCEDIR, 'order')
    with open(chapter_order_file, 'r') as chaptersfile:
        chapters = chaptersfile.read().splitlines()

    for i, ch_dir in enumerate(chapters, start=1):
        # read the caption of the chapter
        caption_file_path = os.path.join(SOURCEDIR, ch_dir, 'caption')
        with open(caption_file_path, 'r') as captionfile:
            ch_caption = captionfile.read().strip()

        # Now we iterate over the sections
        order_file_path = os.path.join(SOURCEDIR, ch_dir, 'order')
        with open(order_file_path, 'r') as orderfile:
            sections = orderfile.read().splitlines()

        if len(sections) == 0:
            continue

        chapter = Chapter(ch_dir, ch_caption, i)
        toc_structure.chapters.append(chapter)

        for j, sec in enumerate(sections, start=1):
            section = Section(ch_dir, sec, i, j)
            toc_structure.add_section(section)

            # if there are at least two sections added, then we can
            # assign prevpage entries and next page entries
            if len(toc_structure.sections) >= 2:
                toc_structure.sections[-1].prevpage = \
                    toc_structure.sections[-2]

                toc_structure.sections[-2].nextpage = section
                
    toc_structure.chapters[0].sections[0].title = FIRST_PAGE_TITLE
    toc_structure.chapters[0].sections[0].caption = FIRST_PAGE_TITLE

    return toc_structure


if __name__ == "__main__":

    shutil.rmtree('build', ignore_errors=True)
    process_static_resources()

    toc_structure = create_toc_structure()

    # process each chapter and section
    for ch in toc_structure:
        for sec in ch:
            convert_section_to_html(sec)

    home_page_path = os.path.join(BUILDDIR, 'index.html')
    shutil.copy(toc_structure.chapters[0].sections[0].target_file, home_page_path)
