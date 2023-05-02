"""
This code can do two things. Firstly (and primarily) it is designed to run as a script to download a textfile
list of coordinates from the DECaLS data server. Secondly, the download function can be imported into any
python code and used on its own to add more flexibility.
"""

# MAIN IMPORTS
import os
import urllib.request as urlib
import argparse
import pandas as pd
from dl import queryClient as qc
from dl.helpers.utils import convert

# MULTITHREADING
from multiprocessing import Pool
import warnings

warnings.filterwarnings("ignore")

# DEFINE A FEW PARAMETERS
outputs = os.getcwd()
url = "https://www.legacysurvey.org/viewer/ls-dr9/cat.fits?ralo={}&rahi={}&declo={}&dechi={}"
query = "SELECT {} FROM ls_dr9.tractor WHERE ra>{} AND ra<{} AND dec>{} AND dec<{}"


# DOWNLOAD FUNCTIONS
def sql_cat(ra, dec, size=0.03, columns="ra, dec", verbose=False):
    """Load data directly into a pandas dataframe from the SQL database.

    Args:
        ra (float): Center coordinate of cutout
        dec (float): Center coordinate of cutout
        size (float, optional): Diameter (width) of the cutout. Defaults to 0.03.
        verbose (bool, optional): Verbose? Defaults to False.

    Returns:
        Pandas DataFrame with catalog info
    """

    # Explicitly calculate the bounds of the cutout.
    ra_min = ra - (size / 2)
    ra_max = ra + (size / 2)
    dec_min = dec - (size / 2)
    dec_max = dec + (size / 2)

    # If overwrite==False and and file exists, don't download. Otherwise, download the file.
    response = qc.query(
        adql=query.format(columns, ra_min, ra_max, dec_min, dec_max), fmt="csv"
    )
    df = convert(response)
    if verbose:
        print("\x1b[33m Catalog at [", ra, dec, "] already exists. \x1b[0m")
    return df


def download_cat(
    ra,
    dec,
    size=0.03,
    download_folder="/catalogs",
    download_name="",
    overwrite=False,
    verbose=False,
):
    """Download catalog into a specified folder.

    Args:
        ra (float): Center coordinate of cutout
        dec (float): Center coordinate of cutout
        size (float, optional): Diameter (width) of the cutout. Defaults to 0.03.
        download_folder (string, optional): Name of the folder to place the catalog into. Defaults to '/catalogs'.
                                            Use '' to place the catalog in the current directory.
        download_name (string, optional): Name of the folder to place the catalog into. Defaults to ''.
                                          If empty (such as in default case), catalogs will be named with ra and dec.
        overwrite (bool, optional): Should we overwrite pre-existing files? Defaults to False.
        verbose (bool, optional): Verbose? Defaults to False.
    """

    # Explicitly calculate the bounds of the cutout.
    ra_min = ra - (size / 2)
    ra_max = ra + (size / 2)
    dec_min = dec - (size / 2)
    dec_max = dec + (size / 2)

    # Get the download destination
    if not os.path.isdir(download_folder[1:]):
        raise ValueError(download_folder + " not found. Does the folder exist?")

    if download_name == "":
        outname = download_folder + "/" + str(ra) + "_" + str(dec) + ".fits"
    else:
        outname = download_folder + "/" + download_name

    # If overwrite==False and and file exists, don't download. Otherwise, download the file.
    if (overwrite == False) & (os.path.isfile(outputs + outname)):
        if verbose:
            print("\x1b[33m Catalog at [", ra, dec, "] already exists. \x1b[0m")
    else:
        try:
            urlib.urlretrieve(
                url.format(ra_min, ra_max, dec_min, dec_max), outputs + outname
            )
        except Exception as e:
            if verbose:
                print(
                    "\x1b[31m Catalog at [", ra, dec, "] failed to download. :( \x1b[0m"
                )
                print(e)
            return None
        if verbose:
            print("\x1b[32m Catalog at [", ra, dec, "] has been downloaded. \x1b[0m")
    return None


# PARSE ARGUMENTS
def argument_parser():
    """Function that parses the arguments passed when running the script.

    Returns:
        ArgumentParser object: the arguments
    """
    result = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    result.add_argument("-n", dest="n_threads", type=int, default=25)
    result.add_argument("-t", dest="textfile", type=str, default="cutout_list.txt")
    result.add_argument("--header", dest="header", type=bool, default=False)
    result.add_argument("-l", dest="length", type=int, default=-10)
    result.add_argument("-v", dest="verbose", type=bool, default=False)
    result.add_argument("-f", dest="folder", type=str, default="/catalogs")
    result.add_argument("-o", dest="overwrite", type=bool, default=False)

    return result


args = argument_parser().parse_args()

# TRY TO IMPORT TQDM PROGRESS BAR
use_fancy_bar = False
if not args.verbose:
    try:
        from tqdm.contrib.concurrent import process_map

        use_fancy_bar = True
    except Exception:
        pass

# LOAD IN THE CATALOG
head = None if args.header == False else 0
# If a txt file (no commas):
if ".txt" in args.textfile:
    cat = pd.read_csv(
        args.textfile,
        header=head,
        names=["ra", "dec", "size", "name"],
        delim_whitespace=True,
    )
    cat = cat.astype({"ra": "float", "dec": "float", "size": "float", "name": "string"})
# If a csv file (comma separated):
elif ".csv" in args.textfile:
    cat = pd.read_csv(
        args.textfile,
        sep=",",
        header=head,
        names=["ra", "dec", "size", "name"],
        skipinitialspace=True,
    )
    cat = cat.astype({"ra": "float", "dec": "float", "size": "float", "name": "string"})
else:
    raise ValueError("Textfile must be either a .txt or .csv file.")


# WRAPPER FUNCTION FOR MULTITHREADING
def download_single_cutout(i):
    """Download a single cutout.

    Args:
        i (int): Index from the text file to download.
    """
    params = cat.iloc[i]
    name = "" if pd.isna(params["name"]) else params["name"]
    size = 0.03 if pd.isna(params["size"]) else params["size"]
    download_cat(
        params["ra"],
        params["dec"],
        size,
        args.folder,
        name,
        args.overwrite,
        args.verbose,
    )
    return None


# MULTITHREADING FUNCTION
def download_all_cutouts():
    """Wrapper for multithreading every cutout."""
    if args.length == -10 or args.length > len(cat):
        inds = len(cat)
    else:
        inds = args.length

    if use_fancy_bar:
        process_map(download_single_cutout, range(inds), max_workers=args.n_threads)
    else:
        with Pool(args.n_threads) as p:
            p.map(download_single_cutout, range(inds))

    return None


# MAIN
if __name__ == "__main__":
    try:
        download_all_cutouts()
        print("Finished!")
    except Exception as e:
        print(e)
