===========================================
Interactively removing bad data points
===========================================

Timeseries derived from SP2 data, such as particle size distributions
from :func:`pysp2.util.process_psds`, occasionally contain artifacts
(instrument dropouts, contamination events, and so on) that are easiest
to identify and remove by eye. :class:`pysp2.vis.DataEditor` provides an
interactive matplotlib-based tool for doing exactly that, without having
to hand-write index-based filtering code.

Launching the editor
-----------------------

``DataEditor`` attaches itself to an existing matplotlib line plot. First
make the plot as usual, keeping a reference to the ``Line2D`` object that
is returned:

.. code-block:: python

    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(ncols=1)
    line, = my_psds['NumConcIncan'].plot(ax=axs)

    browser = pysp2.vis.DataEditor(fig, axs, line)
    plt.show()

You can freely zoom and pan using the normal matplotlib toolbar buttons
before and after making edits.

Deleting a range of points
------------------------------

With the plot window focused, use the following key presses:

* **[d]** — start deleting. The plot title changes to prompt you to pick
  an x-range.
* Left-click twice on the plot to mark the start and end of the range you
  want to remove. The points that will be deleted are highlighted in red,
  and the title shows how many points were selected.
* **[y]** — confirm the deletion. The highlighted points are set to
  ``NaN`` in the plotted line (and therefore in the underlying data, since
  the line shares its data with the array that produced it).
* **[n]** — discard the selection instead of deleting it.

Right-clicking while picking points resets the current selection so you
can start over.

Reading back the edits
--------------------------

Every accepted deletion is recorded in ``browser.data_edits['x_range']``
as a list of ``[start, stop]`` pairs in ``numpy.datetime64`` format:

.. code-block:: python

    browser.data_edits['x_range']
    # [[numpy.datetime64('2023-07-21T12:00:00.000000'),
    #   numpy.datetime64('2023-07-21T12:05:00.000000')],
    #  ...]

Since the edits are applied directly to the ``Line2D``'s y-data, and that
data is the same array backing the xarray ``DataArray`` you plotted, the
edited values are reflected in ``my_psds`` once you are done — no
additional step is needed to apply the edits back to the dataset. The
recorded ``x_range`` list is useful for keeping an audit trail of what was
removed and why, or for re-applying the same edits to a re-processed
version of the dataset with :meth:`xarray.Dataset.sel`.
