# A Methods Focused Guide to Quantum Error Correction and Fault-Tolerant Quantum Computation

This is a mini-book for a senior undergrad or junior graduate student who is already familiar with the fundamentals of quantum computing. This book is authored by [Abdullah Khalid](https://abdullahkhalid.com/).

To read this book, clone this repository and open `contents.ipynb`.

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
The code cells of this book are licensed under [GPLV3](https://www.gnu.org/licenses/gpl-3.0.txt). The non-code portions are licensed under  [Creative Commons Attribution-NonCommercial-NoDerivs ](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode).
