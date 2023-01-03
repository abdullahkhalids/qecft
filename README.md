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

## Building

I use python3.10 for building the book. To build the book, ideally first create a virtual environment, and activate it.
```
virtualenv -p python3.10 ../envqecft
source ../envqecft/bin/activate
```

Then install dependencies and then run the creation script.
```
pip install -r requirements.txt
python ./bookcreator.py
```
To quickly rebuild the book, run `make`. This will also minify the css files.


## License

* The theme, is derived from [sphinx-book-theme](https://github.com/executablebooks/sphinx-book-theme), and the folder `website-jinja-template` and `static/css/screen.css` are licensed under the [3-Clause BSD License](LICENSE-bsd-3-clause) license.
* The non-code portions of the notebooks are licensed under  [Creative Commons Attribution-NonCommercial-NoDerivs ](LICENSE-CC-BY-NC-ND).
* The code cells of this book and any other code in the repository is licensed under [GPLV3](LICENSE-GPL3).


