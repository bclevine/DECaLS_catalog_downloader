# DECaLS_catalog_downloader
A script to quickly download large batches of catalogs from the [DECaLS survey](https://www.legacysurvey.org/dr9/description/) data server. The downloading code may also be easily imported into other Python scripts or Jupyter notebooks for greater control over the download process.

## Dependencies 
The catalog downloader requires the following packages, which come with standard Conda distributions: *os, urllib, argparse, multiprocessing,* and *pandas*.
The downloader optionally uses *[tqdm](https://github.com/tqdm/tqdm)* to implement a progress bar. tqdm can be installed through `pip install tqdm`. If tqdm is not installed, the script should fall back to default multithreading, but I have not actually tested this...

## Running the Script
### Download the Repository
First, download this repository onto your device. You can either manually download, or navigate to your chosen directory and run:

```
git clone https://github.com/bclevine/DECaLS_catalog_downloader.git
```

### Put Coordinates into Textfile
Once this is done, copy your coordinate list into a textfile. An example file comes with this distribution, but if you would like to use a different one (or have multiple in the directory) you can specify the name of the file when running the code. The row structure of the file should be as follows: `ra_coordinate dec_coordinate size_of_cutout name_of_cutout`

**Notes:**

1. The file MUST either have a .txt or .csv extension. 
2. For .txt files, you can use spaces and/or tabs to separate the entries. For .csv files, you must use commas to separate the entries.
4. The textfile can have as many rows as you'd like. 
5. The size of the cutout is optional. If no size is provided. each cutout will be 0.03 square degrees.
6. The name of the cutout is optional. If no name is provided, each cutout will be named after its ra and dec position. 
8. Custom file names *cannot* contain spaces. 
9. It's recommended (but not required) to include the .fits extension in the custom name, as the script will not append that on its own. 
10. The file can have a header, but you will have to specify that when running the script (see below).
11. The size of the cutout is its width in degrees. 

To easily make the textfile, I recommend making a Google sheet or Excel spreadsheet with all the values you want, and then just copy/pasting that into the txt file.

### Run the Script
It's time to run the script. In your terminal, navigate to the directory and type the following command:

```
python3 download_catalogs.py
```

The following flags are available:
1. *-n [number of threads]* : How many threads should be used for multithreading? More threads will usually be faster. Defaults to 25.
2. *-t [textfile name]* : Name of textfile to pull coordinates from. Defaults to 'cutout_list.txt'.
3. *--header [boolean]* : Whether or not the textfile has a header. Defaults to False.
4. *-f [download folder]* : Name of the folder in which to place catalog downloads. Defaults to '/catalogs'. Use '' to place downloads in the top-level directory.
5. *-l [length of coordinate list]* : For testing, you may not want to download the entire catalog from your textfile. This number will cap the list at a certain index — for example, `-l 5` will download the first 5 coordinates from the list. Leave the flag blank to download the entire textfile.
6. *-o [overwrite]* : By default, the script will skip any catalogs with duplicate names in the download folder. Overwrite will force it to overwrite any pre-existing catalogs. Defaults to False.
7. *-v [verbose]* : Use verbose output? Defaults to False. If True, the progress bar will be disabled.

For example, the following command will use 10 threads, download the first 60 coordinates in the textfile, and place downloads in the folder '/all_catalogs'.

```
python3 download_catalogs.py -n 10 -l 60 -f '/all_catalogs'
```

## Usage as a Python Module
You can use this script as a module for another script or a Jupyter notebook by placing it in the top-level directory. The usable function is `download_cat(ra, dec, size=0.03, download_folder='/catalogs', download_name='', overwrite=False, verbose=False)` and has the following arguments:

* ra (float): Center coordinate of cutout
* dec (float): Center coordinate of cutout
* size (float, optional): Diameter (width) of the cutout in degrees. Defaults to 0.03.
* download_folder (string, optional): Name of the folder to place the catalog into. Defaults to '/catalogs'. Use '' to place the catalog in the current directory.
* download_name (string, optional): Name of the folder to place the catalog into. Defaults to ''. If empty (such as in default case), catalogs will be named with ra and dec.
* overwrite (bool, optional): Should we overwrite pre-existing files? Defaults to False.
* verbose (bool, optional): Verbose? Defaults to False.

For example:

```
from download_catalogs import download_cat

download_cat(100, 30, overwrite=True)
download_cat(101, 31, download_folder='', verbose=True)
```

## Troubleshooting
Some systems may encounter an SSL verification error when trying to download catalogs. You can recognize this issue if you see something like `[SSL: CERTIFICATE_VERIFY_FAILED]` when running in verbose mode. One potential workaround is to add the following code after the `#MULTITHREADING` block in `download_catalogs.py'. Thanks to Ruoyang (Murphy) Tu for finding this solution:
​
```
#SSL ERROR FIXING
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```
