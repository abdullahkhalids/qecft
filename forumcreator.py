# !/usr/bin/env python3
"""Creates pages for tasks with Isso comments."""

import os
import nbformat
import shutil
from nbconvert import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor, RegexRemovePreprocessor
from traitlets.config import Config
from jinja2 import Environment, FileSystemLoader

# Configuration variables
SITEURL = 'http://localhost:8000/'
LISTENURL = 'http://localhost:8017/'
SOURCEDIR = 'tasks'
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

# Nbconvert config
c = Config()
c.TagRemovePreprocessor.enabled = True
c.TagRemovePreprocessor.remove_cell_tags = ("remove-cell",)
c.RegexRemovePreprocessor.enabled = True
c.RegexRemovePreprocessor.patterns = r'\s*\Z'
c.HTMLExporter.template_name = "jupyter-html-template"

html_exporter = HTMLExporter(config=c)
html_exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)
html_exporter.register_preprocessor(RegexRemovePreprocessor(config=c), True)
html_exporter.anchor_link_text = '#'

# Jinja config
file_loader = FileSystemLoader('website-jinja-template')
env = Environment(loader=file_loader, **jinja2_config)
template = env.get_template('page.html')

def generate_home():
    """Generate the home index.html page."""
    target_file = os.path.join(BUILDDIR, 'index.html')

    # You can modify the content of the home page as needed
    content = """
    <html>
    <head>
        <title>Tasks</title>
    </head>
    <body>
        <h1>Welcome to the Tasks Page</h1>
        <p>This is the home page of your website.</p>
        <p>Checkout /task-1 or /task-2 to view tasks</p>
    </body>
    </html>
    """

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)

# change the localhost:8017 according to your respective Listen URL in isso.cfg
ISSO_CONFIG = """
<div id="isso-thread"></div>
<script src="//localhost:8017/js/embed.min.js"></script>
<script>
    var issoConfig = {
        'host': 'http://localhost:8017/',
        'target': 'isso-thread',
        'thread': '{{ request.path }}',
    };
</script>
"""

def convert_task_to_html(task_number, question):
    """Convert task to HTML page."""
    task_title = f"Task {task_number}"
    target_dir = os.path.join(BUILDDIR, f"task-{task_number}")
    target_file = os.path.join(target_dir, 'index.html')
    url = f"task-{task_number}"
    content = f"<h1>{task_title}</h1>\n\n{question}\n{ISSO_CONFIG}"

    os.makedirs(target_dir, exist_ok=True)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)

def process_static_resources():
    """Copy static resources into the build folder."""
    for name in STATIC_FOLDERS:
        shutil.copytree(name, os.path.join(BUILDDIR, name))

if __name__ == "__main__":
    print("Converting tasks to HTML pages...")
    print("Deleting existing build directory")
    shutil.rmtree('build', ignore_errors=True)
    
    print(f"Copying folders: {STATIC_FOLDERS}")
    process_static_resources()

    tasks = os.listdir(SOURCEDIR)
    for task in tasks:
        task_file = os.path.join(SOURCEDIR, task)
        with open(task_file, 'r', encoding='utf-8') as f:
            question = f.read()

        task_number = os.path.splitext(task)[0]
        convert_task_to_html(task_number, question)

    print("Generating Home page")
    generate_home()

    print("HTML conversion complete")
