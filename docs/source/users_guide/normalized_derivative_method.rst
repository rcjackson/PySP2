========================================================
Estimating incident irradiance (Moteki & Kondo method)
========================================================

Particles that evaporate while passing through the SP2's laser beam
produce a scattering signal that does not follow the beam's true Gaussian
intensity profile, which biases both LEO-fits and standard Gaussian fits.
Moteki & Kondo (2008, *Method to measure time-dependent scattering cross
sections of particles evaporating in a laser beam*, Journal of Aerosol
Science, 39(4), 348-364) describe a technique for recovering the
time-dependent scattering cross section, and with it, an estimate of the
normalized incident laser irradiance the particle actually experienced,
by examining the normalized derivative of the scattering signal.
:mod:`pysp2.util` implements this method as a short pipeline of
functions.

Configuring the method
------------------------

The method's noise model is controlled by a :class:`pysp2.util.MLEConfig`
object, which bundles the instrument's time resolution and the
noise/calibration coefficients used in Moteki & Kondo's Appendix A:

.. code-block:: python

    config = pysp2.util.MLEConfig(
        h=0.4, sigma_bar=2.5, delta_sigma=0.3,
        A1=100.0, A2=0.02, A3=0.0005,
    )

``grid_size`` and ``grid_margin`` control the resolution and extent of the
grid search used to maximize the likelihood over tau (see below); their
defaults are reasonable for most SP2 datasets.

Computing the normalized derivative
--------------------------------------

The first step is computing the normalized derivative :math:`(1/S)\,dS/dt`
of each particle's scattering signal, using :func:`pysp2.util.central_difference`:

.. code-block:: python

    my_sp2b = pysp2.io.read_sp2(pysp2.testing.EXAMPLE_SP2B)
    my_ini = pysp2.io.read_config(pysp2.testing.EXAMPLE_INI)
    my_binary = pysp2.util.gaussian_fit(my_sp2b, my_ini)

    norm_deriv = pysp2.util.central_difference(my_sp2b)

``my_binary`` (the Gaussian-fit output containing ``PkStart_ch#``,
``PkPos_ch#``, and ``PkFWHM_ch#``) is needed later to restrict the method
to the leading edge of each peak. The normalized derivative for a single
particle and channel can be inspected with
:func:`pysp2.util.plot_normalized_derivative`:

.. code-block:: python

    pysp2.util.plot_normalized_derivative(my_sp2b, norm_deriv, record_no=0, chn=0,
                                           plot_scattering_signal=True)

Estimating tau and the statistical distance d\ :sup:`2`
-----------------------------------------------------------

For a single particle (``event_index``), :func:`pysp2.util.mle_tau_moteki_kondo`
performs a grid-search maximum-likelihood estimate of tau (the time at
which the particle crosses the peak of the beam) for every ``p``-point
subset of samples on the leading edge of the peak:

.. code-block:: python

    tau_hat = pysp2.util.mle_tau_moteki_kondo(
        my_binary, norm_deriv, p=11, ch='Data_ch0', event_index=0, config=config,
    )

:func:`pysp2.util.compute_d2_moteki_kondo` then computes the statistical
distance d\ :sup:`2`\ (k) (Moteki & Kondo, Eq. A.11) for each of those
subsets, measuring how well each one matches the expected linear
behavior of a particle crossing a Gaussian beam:

.. code-block:: python

    d2 = pysp2.util.compute_d2_moteki_kondo(
        my_binary, norm_deriv, tau_hat, p=11, ch='Data_ch0', event_index=0, config=config,
    )

Estimating the beam width sigma
----------------------------------

:func:`pysp2.util.compute_sigma_moteki_kondo` selects the subset ``kbest``
that minimizes d\ :sup:`2`, and uses it to fit the Gaussian beam width
sigma via weighted least squares. It returns a small Dataset with
``sigma_hat``, ``tau_best``, ``kbest``, ``d2_best``, and ``accepted`` (a
flag for whether ``d2_best`` was below the acceptance threshold used in
the paper):

.. code-block:: python

    sigma_out = pysp2.util.compute_sigma_moteki_kondo(
        my_binary, norm_deriv, tau_hat, d2, p=11, ch='Data_ch0', event_index=0, config=config,
    )

Computing normalized incident irradiance
-------------------------------------------

Once ``sigma_hat`` and ``tau_best`` are known, the normalized incident
irradiance :math:`I(t)/I_0` follows directly from the Gaussian beam model
(Moteki & Kondo, Eq. 1), via
:func:`pysp2.util.compute_normalized_incident_irradiance_moteki_kondo`:

.. code-block:: python

    irradiance = pysp2.util.compute_normalized_incident_irradiance_moteki_kondo(sigma_out)

The whole fit — the normalized derivative, the expected :math:`I'(t)/I(t)`
line, the scattering signal, and the recovered normalized incident
irradiance — can be visualized together with
:func:`pysp2.util.plot_incident_irradiance`:

.. code-block:: python

    pysp2.util.plot_incident_irradiance(
        my_sp2b, norm_deriv, record_no=0, chn=0, sigma_ds=sigma_out,
    )
