#!/home/abdullah/Apps/miniconda3/bin/python
"""Creates a book out of a collection of jupyter notebooks."""

import shutil
import os
import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor, RegexRemovePreprocessor
from traitlets.config import Config
from jinja2 import Environment, FileSystemLoader


## Config variables for website
SITEURL = 'https://abdullahkhalid.com/qecft'
#SITEURL = 'http://localhost:8000'


SITENAME = 'A Methods Focused Guide to Quantum Error Correction and Fault-Tolerant Quantum Computation'
REPOSITORY = 'https://github.com/abdullahkhalids/qecft'

SOURCEDIR = 'chapters'
# Section titles are drawn from the first cell of the notebook
# But for the first section, we add a custom caption.
FIRST_SECTION_TITLE = 'About this book'

BUILDDIR = 'build'
STATIC_FOLDERS = ['static', 'images']

jinja2_config = {
    'comment_start_string': '<!--',
    'comment_end_string': '-->',
    'trim_blocks': True,
    'lstrip_blocks': True,
    'keep_trailing_newline': True,
    'extensions': []
}

## Nbconvert config
# These are the config settings for converting the contents of
# the notebook to html via nbconvert
c = Config()
# Remove any cell marked with this tag
c.TagRemovePreprocessor.enabled = True
c.TagRemovePreprocessor.remove_cell_tags = ("remove-cell",)
# remove any empty cells using this regexp
c.RegexRemovePreprocessor.enabled = True
c.RegexRemovePreprocessor.patterns = r'\s*\Z'
# The template for nbconvert to html is stored in this folder
c.HTMLExporter.template_name = "jupyter-html-template"

html_exporter = HTMLExporter(config=c)
html_exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)
html_exporter.register_preprocessor(RegexRemovePreprocessor(config=c), True)
html_exporter.anchor_link_text = '#'

## Jinja config
# The jinja template is used to render the converted notebook html
# into a complete html page.
# The template is stored in the following folder and file
file_loader = FileSystemLoader('website-jinja-template')
env = Environment(loader=file_loader, **jinja2_config)
template = env.get_template('page.html')



## Various classes to make our life easier
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

        # This is one place where the heavy lifting is done
        # this converts notebook contents to html
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

# The jinja template system needs a dictionary of variables
# to render the contents properly
j2_vars = {
    'SITENAME': SITENAME,
    'SITEURL': SITEURL,
    'REPOSITORY': REPOSITORY,
    'page': '',
    'toc': ''
}


def convert_section_to_html(section):
    """Convert ipynb to html."""
    j2_vars['page'] = section
    j2_vars['toc'] = toc_structure

    os.makedirs(section.target_dir)
    with open(section.target_file, 'w') as f:
        # convert the section into html and write to file
        f.write(template.render(**j2_vars))


def process_static_resources():
    """Copy static resources into the build folder."""
    for name in STATIC_FOLDERS:
        shutil.copytree(name,
                        os.path.join(BUILDDIR, name))


def create_toc_structure():
    """Determine the structure of the book."""

    toc_structure = Toc()
    # read the order file to determine the order of the chapters
    chapter_order_file = os.path.join(SOURCEDIR, 'order')
    with open(chapter_order_file, 'r') as chaptersfile:
        chapters = chaptersfile.read().splitlines()

    # Now iterate over the chapters
    for i, ch_dir in enumerate(chapters, start=1):
        # read the caption of the chapter
        caption_file_path = os.path.join(SOURCEDIR, ch_dir, 'caption')
        with open(caption_file_path, 'r') as captionfile:
            ch_caption = captionfile.read().strip()

        # Now we iterate over the sections
        order_file_path = os.path.join(SOURCEDIR, ch_dir, 'order')
        with open(order_file_path, 'r') as orderfile:
            sections = orderfile.read().splitlines()

        # if empty chapter, don't add to toc
        if len(sections) == 0:
            continue

        # create and add chapter to toc
        chapter = Chapter(ch_dir, ch_caption, i)
        toc_structure.chapters.append(chapter)

        # Iterate over sections in chapter
        for j, sec in enumerate(sections, start=1):
            # create and add chapter to toc
            section = Section(ch_dir, sec, i, j)
            toc_structure.add_section(section)

            # if there are at least two sections added, then we can
            # assign prevpage entries and next page entries
            if len(toc_structure.sections) >= 2:
                # for the latest added section, previous page should be
                # second latest section.
                toc_structure.sections[-1].prevpage = \
                    toc_structure.sections[-2]

                # And for second latest section, the next page should
                # be this section
                toc_structure.sections[-2].nextpage = \
                    toc_structure.sections[-1]
                
    # Fix the caption for the first section
    toc_structure.chapters[0].sections[0].title = FIRST_SECTION_TITLE
    toc_structure.chapters[0].sections[0].caption = FIRST_SECTION_TITLE

    return toc_structure


if __name__ == "__main__":

    print("Converting to HTML now...")
    print("Deleting existing build directory")
    shutil.rmtree('build', ignore_errors=True)
    
    print(f"Copying folders: {STATIC_FOLDERS}")
    process_static_resources()

    print("Creating toc structure from order and caption files")
    toc_structure = create_toc_structure()

    # process each chapter and section
    print("Converting each section to a html page\n")
    for ch in toc_structure:
        for sec in ch:
            print(f'{sec.ch_index}.{sec.index} {sec.caption}')
            convert_section_to_html(sec)
    print("")

    print("Setting first section as index.html")
    home_page_path = os.path.join(BUILDDIR, 'index.html')
    shutil.copy(toc_structure.chapters[0].sections[0].target_file, home_page_path)
    print("html build complete\n")
