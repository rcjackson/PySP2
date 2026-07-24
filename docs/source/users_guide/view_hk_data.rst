Viewing housekeeping data
=========================

PySP2 contains built-in modules for loading and viewing SP2 housekeeping files with
a .hk extension. These housekeeping files are then converted into xarray Datasets so that they
can be easily analyzed and plotted.
In order to load a housekeeping file, one simply does the following command:

.. code-block:: python

    my_hk = pysp2.io.read_hk_file(pysp2.testing.EXAMPLE_HK)

The :func:`pysp2.io.read_hk_file` function returns a standard xarray dataset. All of the variables
are 1 Hz timeseries. Therefore, each one of the variables in the xarray dataset can be visualized
using the standard xarray routines like this:

    my_hk['Num of Particles'].plot()
    plt.show()

.. image:: num_of_particles.png

Reading multiple housekeeping files at once
---------------------------------------------

A field deployment will typically produce many .hk files, one per
acquisition session. Rather than looping over :func:`pysp2.io.read_hk_file`
and concatenating the results by hand, :func:`pysp2.io.read_multi_hk_file`
accepts a glob pattern and returns a single, time-sorted Dataset:

.. code-block:: python

    my_hk = pysp2.io.read_multi_hk_file('/data/my_campaign/*.hk')

This works for both the classic SP2's tab-separated .hk files as read by
:func:`pysp2.io.read_hk_file`.

For the newer SP2-XR instrument, housekeeping files use a different format
and are read with :func:`pysp2.io.read_sp2xr_hk_file` instead; see
:doc:`sp2xr_data` for details.

