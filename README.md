# DECaLS_catalog_downloader
A script to quickly download large batches of catalogs from the [DECaLS survey](https://www.legacysurvey.org/dr9/description/) data server. The downloading code may also be easily imported into other Python scripts or Jupyter notebooks for greater control over the download process.

## Dependencies 
The catalog downloader requires the following packages, which come with standard Conda distributions: os, urllib, argparse, multiprocessing, and pandas.
The downloader optionally uses [tqdm](https://github.com/tqdm/tqdm) to implement a progress bar. tqdm can be installed through `pip install tqdm`. If tqdm is not installed, the script should fall back to default multithreading, but I have not actually tested this...

## Running the Script
Begin by copying your coordinate list into a textfile. An example file comes with this distribution, but if you would like to use a different one (or have multiple in the directory) you can specify the name of the file when running the code. The structure of the file should be as follows:
```ra_coordinate dec_coordinate size_of_cutout name_of_cutout```
