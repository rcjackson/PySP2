""" I/O function for reading .dat files from original IGOR processing."""

import xarray as xr
import pandas as pd
import numpy as np
import act
import platform
import os

from glob import glob
from datetime import datetime, timedelta

def read_dat(file_name, type):
    """
    This reads the .dat files that generate the intermediate parameters used
    by the Igor processing. Wildcards are supported.

    Parameters
    ----------
    file_name: str
        The name of the file to save to. Use a wildcard to open multiple files at once.
    type: str
        This parameter must be one of:
            'particle': Load individual particle timeseries from .dat file
            'conc': Load timeseries of concentrations.
    Returns
    -------
    ds: xarray Dataset
        The xarray dataset to store the parameters in.
    """

    if type.lower() not in ['particle', 'conc']:
        raise ValueError("Invalid input for type, must be either 'particle' or 'conc'!")

    fname = glob(file_name, recursive=True)
    ds_list = []
    for f in fname:
        try:
            if type.lower() == 'particle':
                ds = act.io.csvfiles.read_csv(f, sep="\t", skiprows=2)
            else:
                ds = act.io.csvfiles.read_csv(f, sep="\t")
            ds_list.append(ds)
        except (pd.errors.EmptyDataError, IndexError):
            continue
    if type.lower() == 'particle':
        return xr.concat(ds_list, dim='index').sortby('DateTimeWave')
    elif type.lower() == 'conc':
        return xr.concat(ds_list, dim='index').sortby('Start DateTime')


def read_calibration(directory):
    """
    This reads data from a bead calibration from the SP2. Each dataset is stored
    in a dictionary whose keys correspond to a given scattering or incadescence
    diameter in nm.

    Parameters
    ----------
    directory: str
        The path to the calibration data. The directory must contain processed .dat
    files for each segment as well as .txt files that describe what diameter each
    .dat file corresponds to.

    Returns
    -------
    my_dat: dict
        A dictionary storing the dataset for each scattering/incadescence diameter.
    """

    file_list = glob(os.path.join(directory, '*'))
    # Look for dataset date
    for f in file_list:
        if platform.system() == "Windows":
            file_name = f.split("\\")[-1]
        else:
            file_name = f.split("/")[-1]

        date_str = file_name[0:8]
        if date_str.isnumeric():
            dt = datetime.strptime(date_str, '%Y%m%d')
            break

    # First load the dataset scattering and incadesence diameters
    scat_ds = pd.read_csv(os.path.join(directory, '%sExptDetail_Scat.txt' % date_str), sep='\t')
    in_ds = pd.read_csv(os.path.join(directory, '%sExptDetail_Aq.txt' % date_str), sep='\t')

    scat_diam = scat_ds.Diameter.values
    incan_diam = in_ds.Diameter.values
    calibration_data = {}
    for i in range(len(scat_diam)):
        my_ds = []
        for j in range(scat_ds["FileStart"][i], scat_ds["FileEnd"][i]+1):
            my_ds.append(read_dat(os.path.join(directory, '%sx%03d.dat' % (date_str, j)), type='particle'))
        calibration_data["scat_%d" % scat_diam[i]] = xr.concat(my_ds, dim='index').sortby('DateTimeWave')

    for i in range(len(incan_diam)):
        my_ds = []
        for j in range(in_ds["FileStart"][i], in_ds["FileEnd"][i]+1):
            my_ds.append(read_dat(os.path.join(directory, '%sx%03d.dat' % (date_str, j)), type='particle'))
        calibration_data["incan_%d" % incan_diam[i]] = xr.concat(my_ds, dim='index').sortby('DateTimeWave')

    del scat_ds
    del in_ds

    return calibration_data
