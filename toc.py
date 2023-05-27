"""Create a contents notebook."""

import nbformat
import bookcreator
import sys

# create a new notebook
nb = nbformat.v4.new_notebook()

title_str = f'# {bookcreator.SITENAME}'
cell = nbformat.v4.new_markdown_cell(title_str)
nb['cells'].append(cell)


# create table of contents
toc_structure = bookcreator.create_toc_structure()

contents_str = '## Table of Contents\n\n'

for i, ch in enumerate(toc_structure.chapters):
    contents_str += f'### {i+1}. {ch.caption}\n\n'

    for j, sec in enumerate(ch):
        contents_str += f'[{i+1}.{j+1} {sec.caption}]({sec.source})\n\n'

    contents_str += '\n'

cell = nbformat.v4.new_markdown_cell(contents_str)
nb['cells'].append(cell)


# fill in remaining details into the notebook and write it
kernelspec = {
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
    "name": "python3"
}

nb['metadata']['kernelspec'] = kernelspec

language_info = {
    "codemirror_mode": {
        "name": "ipython",
        "version": 3
    },
    "file_extension": ".py",
    "mimetype": "text/x-python",
    "name": "python",
    "nbconvert_exporter": "python",
    "pygments_lexer": "ipython3",
    "version": f"{sys.version.split(' ', maxsplit=1)[0]}"
}

nb['metadata']['language_info'] = language_info


nbformat.write(nb, 'contents.ipynb')
