=========================
Working with SP2-XR data
=========================

In addition to the original SP2, PySP2 can read data from the newer SP2-XR
instrument. The SP2-XR writes the same three kinds of files as the SP2
(raw waveforms, housekeeping, and configuration), plus an additional
Particle-by-Particle (PbP) file in which the instrument firmware has
already performed the peak fitting on-board. All of the SP2-XR readers
accept either the raw .csv file or a .zip archive containing it.

Reading raw waveforms
----------------------

Just like the original SP2's :func:`pysp2.io.read_sp2`, SP2-XR waveform
files are read with :func:`pysp2.io.read_sp2xr`:

.. code-block:: python

    my_sp2xr = pysp2.io.read_sp2xr(pysp2.testing.EXAMPLE_SP2XR_SP2B)

This returns an xarray Dataset with the same "Data_chx" waveform layout
used by the rest of PySP2, so it can be fed directly into
:func:`pysp2.util.gaussian_fit` and :func:`pysp2.vis.plot_wave`.

Reading housekeeping data
--------------------------

The SP2-XR housekeeping file uses a different (comma-separated) format
than the original SP2's tab-separated .hk file, so it has its own reader,
:func:`pysp2.io.read_sp2xr_hk_file`:

.. code-block:: python

    my_hk = pysp2.io.read_sp2xr_hk_file(pysp2.testing.EXAMPLE_SP2XR_HK)

The returned Dataset follows the same time-indexed convention as
:func:`pysp2.io.read_hk_file` (see :doc:`view_hk_data`). The SP2-XR
firmware also computes its own particle size and mass distributions
on-board, storing them as ``Scatter Bin N`` / ``Incand Bin N`` columns in
the HK file; these are excluded from ``read_sp2xr_hk_file`` output (to
keep it comparable to the classic SP2 HK reader) but can be read
separately as a 2-D ``(time, num_bins)`` Dataset with
:func:`pysp2.io.read_sp2xr_hk_psd`:

.. code-block:: python

    my_psd = pysp2.io.read_sp2xr_hk_psd(pysp2.testing.EXAMPLE_SP2XR_HK)

``my_psd`` contains ``ScatNumEnsemble`` and ``IncanNumEnsemble`` raw
particle counts per bin per time; divide by the sample volume for that
record (``Sample Flow Controller Read (vccm) / 60``) to get concentration.

Both HK readers retain the retained firmware-computed "Scattering Mass
Conc" and "Incand Mass Conc" columns. Since these are derived from an
on-board calibration curve, the calibration files that sit alongside the
HK file on disk (matching ``*_Scatt_*.csv`` and ``*_Incan_*.csv``) are
automatically located and attached to the returned Dataset's attributes
(``ScatCalibration_Diameter_nm``, ``ScatCalibration_Signal``,
``IncanCalibration_Mass_fg``, ``IncanCalibration_Signal``, and the source
file paths) for provenance. A warning is raised if a calibration file
cannot be found next to the HK file.

Reading particle-by-particle files
------------------------------------

Because the SP2-XR firmware performs peak fitting on-board, per-particle
peak heights, positions, widths, transit times, and pre-calibrated optical
diameter / incandescence mass are all available directly from the PbP
file, with no separate gaussian-fit step required. Read a PbP file with
:func:`pysp2.io.read_sp2xr_pbp`:

.. code-block:: python

    my_pbp = pysp2.io.read_sp2xr_pbp(pysp2.testing.EXAMPLE_SP2XR_PBP)

The PbP columns are renamed to match PySP2's own peak-fit output
(``PkHt_ch0``, ``PkHt_ch1``, ``PkFWHM_ch0``, ...) so that ``my_pbp`` can be
passed to the same downstream calibration utilities used for classic SP2
data, such as :func:`pysp2.util.calc_diams_masses`, provided appropriate
SP2-XR calibration coefficients.

By default, the firmware's own pre-calibrated ``Scatter Size (nm)`` and
``Incand Mass (fg)`` columns are dropped, to encourage recalibrating with
PySP2's own curves. Pass ``keep_firmware_calibration=True`` to retain them
(as ``firmware_ScatterSize_nm`` and ``firmware_IncandMass_fg``); in that
case the matching calibration CSVs are located and attached to the
Dataset's attributes the same way as for the HK readers above.

Each acquisition session on the SP2-XR writes exactly one HK file (always
suffixed ``_x0001``) but may write several PbP files. Since only the HK
file's timestamp can be trusted as an absolute time reference,
``read_sp2xr_pbp`` automatically looks for the matching HK file in the
same directory and uses it to convert the PbP file's relative instrument
timestamps into an absolute ``time`` coordinate. If no matching HK file is
found on disk, a warning is issued and ``my_pbp`` is returned with only
the relative instrument seconds available.

Reading multiple housekeeping files at once
---------------------------------------------

See :doc:`view_hk_data` for :func:`pysp2.io.read_multi_hk_file`, which
also works for concatenating a directory of classic SP2 ``.hk`` files.
