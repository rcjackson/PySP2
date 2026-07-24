=================================
LEO-fits and deadtime correction
=================================

PySP2 includes two corrections that improve the accuracy of particle
sizes and concentrations derived from the standard Gaussian peak fits:
Leading-Edge-Only (LEO) fits, which recover an amplitude estimate for
particles that evaporate before the peak of the laser beam, and a
deadtime bias correction for high particle concentrations.

Leading-Edge-Only (LEO) fits
------------------------------

Incandescing (soot-containing) particles can evaporate before they reach
the peak intensity of the laser beam, which biases a full Gaussian fit to
their scattering signal. The LEO-fit technique corrects for this by only
fitting the leading edge of the peak, using the known shape of the laser
beam (measured from purely-scattering particles) to reconstruct what the
amplitude would have been had the particle not evaporated early.

LEO-fits require two steps. First, :func:`pysp2.util.beam_shape` uses
particles that only scatter light (i.e. that are not incandescing) to
characterize the laser beam profile and the particles' position relative
to the split-detector or the peak of the beam:

.. code-block:: python

    my_binary = pysp2.util.gaussian_fit(waveforms, my_config)
    my_binary = pysp2.util.beam_shape(my_binary, Globals=global_settings)

This adds a set of ``leo_``-prefixed variables to the dataset (see
:doc:`particle_information`) that describe the beam profile and the
window over which the leading-edge fit should be performed. These
variables are interpolated across all particles, so LEO-fits are possible
for incandescing particles as well as purely-scattering ones.

Once the beam shape has been characterized, :func:`pysp2.util.leo_fit`
performs the actual leading-edge fit:

.. code-block:: python

    my_binary = pysp2.util.leo_fit(my_binary, Globals=global_settings)

This adds ``leo_FtAmp_ch0``/``leo_FtAmp_ch4`` (the LEO-fit peak
amplitudes) and ``leo_Base_ch0``/``leo_Base_ch4`` (the LEO-fit
baselines) to the dataset.

In practice, both steps are most conveniently run together by passing
``leo_fits=True`` to :func:`pysp2.util.calc_diams_masses`, which will
call ``beam_shape`` and ``leo_fit`` internally before calculating particle
diameters and masses:

.. code-block:: python

    particles = pysp2.util.calc_diams_masses(my_binary, Globals=global_settings, leo_fits=True)

Deadtime bias correction
--------------------------

At high particle concentrations, the SP2's trigger can miss particles
while it is still processing a previous one, biasing measured
concentrations low. :func:`pysp2.util.deadtime` implements the correction
described in Schwarz et al. (2022, *"Invisible bias" in the single
particle soot photometer due to trigger deadtime*, Aerosol Science and
Technology, 56:7, 623-635, `doi:10.1080/02786826.2022.2064265
<https://doi.org/10.1080/02786826.2022.2064265>`_):

.. code-block:: python

    my_binary = pysp2.util.deadtime(my_binary, my_ini)

This adds a ``DeadtimeRelativeBias`` variable to the dataset, giving the
relative bias in each measurement buffer. This can be used to correct
number and mass concentrations derived downstream (e.g. from
:func:`pysp2.util.process_psds`) for deadtime-induced undercounting at
high concentrations.
