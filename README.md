# A Methods Focused Guide to Quantum Error Correction and Fault-Tolerant Quantum Computation

This is a mini-book for a senior undergrad or junior graduate student who is already familiar with the fundamentals of quantum computing. This book is authored by [Abdullah Khalid](https://abdullahkhalid.com/).

To read this book, clone this repository and open [contents.ipynb](contents.ipynb).

An online copy of the book is available [here](https://abdullahkhalid.com/qecft/)

## Citing

To cite this book, please use the following bibtex entry
```
@book{abdullahkhalid2023,
  title = {A Methods Focused Guide to Quantum Error Correction and Fault-Tolerant Quantum Computation},
  author = {Abdullah Khalid},
  year = 2023,
}
```

## Building the html version

I use python3.10 for building the book. To build the book, ideally first create a virtual environment.
```
python -m pip install virtualenv # if you don't already have this installed
virtualenv -p python3.10 envqecft
source envqecft/bin/activate
```

Then install dependencies.
```
pip install -r requirements.txt
```

Finally, you can build or rebuild the book as follows. 

```
make
```

If you want to host the site locally for testing purposes, open `bookcreator.py` and set `SITEURL = 'http://localhost:8000'`. Then, launch a local web server with

```
python -m http.server -d build
```

## Building the commenting system
Commenting System using Isso
To set up and run the commenting system with Isso, follow these steps:

Start the Flask server by running the following command in your terminal or command prompt:

```bash
python app.py
```
This will start the Flask server and make your website accessible.

Next, start the Isso server. Run the following command in your terminal or command prompt:

```bash
isso -c isso.cfg run
```
This command starts the Isso server using the provided configuration file (isso.cfg).

The Isso server is now running and ready to handle comments. You can visit the host website and test the commenting functionality by leaving comments on the pages.

The dbpath option is set to isso.db, which means the Isso database will be stored in the current directory.

Note: Ensure that the Isso server has write permissions in the current directory to create and access the database file.


## Building the table of contents for the jupyter notebooks
The `contents.ipynb` file is created using the python script `toc.py`. This should be run every time there are any changes in the table of contents. This script depends on two parts. Inside `chapters` and every subfolder there is an `order` file, containing a list of file names. This file specifies the order of the chapters and sections respectively. Inside each subfoler, there is additionally a `caption` file that specifies the name of the chapter, as it appears in the table of contents.

## License

* The theme, is derived from [sphinx-book-theme](https://github.com/executablebooks/sphinx-book-theme), and the folder `website-jinja-template` and `static/css/screen.css` are licensed under the [3-Clause BSD License](LICENSE-bsd-3-clause) license.
* The non-code portions of the notebooks are licensed under  [Creative Commons Attribution-NonCommercial-NoDerivs ](LICENSE-CC-BY-NC-ND).
* The code cells of this book and any other code in the repository is licensed under [GPLV3](LICENSE-GPL3).

## Acknowledgements

The initial drafts of this book were produced with the help of a grant by the [Unitary Fund](https://unitary.fund/grants.html).


