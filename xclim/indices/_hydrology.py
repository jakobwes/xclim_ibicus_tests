import numpy as np
import xarray

from xclim.core.units import declare_units

from . import generic

__all__ = [
    "base_flow_index",
    "rb_flashiness_index",
    "snd_max_doy",
]


@declare_units(q="[discharge]")
def base_flow_index(q: xarray.DataArray, freq: str = "YS"):  # noqa: D401
    r"""Base flow index.

    Return the base flow index, defined as the minimum 7-day average flow divided by the mean flow.

    Parameters
    ----------
    q : xarray.DataArray
      Rate of river discharge.
    freq : str
      Resampling frequency.

    Returns
    -------
    xarray.DataArray, [dimensionless]
      Base flow index.

    Notes
    -----
    Let :math:`\mathbf{q}=q_0, q_1, \ldots, q_n` be the sequence of daily discharge and :math:`\overline{\mathbf{q}}`
    the mean flow over the period. The base flow index is given by:

    .. math::

       \frac{\min(\mathrm{CMA}_7(\mathbf{q}))}{\overline{\mathbf{q}}}


    where :math:`\mathrm{CMA}_7` is the seven days moving average of the daily flow:

    .. math::

       \mathrm{CMA}_7(q_i) = \frac{\sum_{j=i-3}^{i+3} q_j}{7}

    """
    m7 = q.rolling(time=7, center=True).mean(skipna=False).resample(time=freq)
    mq = q.resample(time=freq)

    m7m = m7.min(dim="time")
    out = m7m / mq.mean(dim="time")
    out.attrs["units"] = ""
    return out


@declare_units(q="[discharge]")
def rb_flashiness_index(q: xarray.DataArray, freq: str = "YS"):  # noqa: D401
    r"""Richards-Baker flashiness index.

    Measures oscillations in flow relative to total flow, quantifying the frequency and rapidity of short term changes
    in flow.

    Parameters
    ----------
    q : xarray.DataArray
      Rate of river discharge.
    freq : str
      Resampling frequency.

    Returns
    -------
    xarray.DataArray, [dimensionless]
      R-B Index.

    Notes
    -----
    Let :math:`\mathbf{q}=q_0, q_1, \ldots, q_n` be the sequence of daily discharge, the R-B Index is given by:

    .. math::

       \frac{\sum_{i=1}^n |q_i - q_{i-1}|}{\sum_{i=1}^n q_i}

    References
    ----------
    Baker, D.B., R.P. Richards, T.T. Loftus, and J.W. Kramer, 2004. A new Flashiness Index: Characteristics and
    Applications to Midwestern Rivers and Streams. Journal of the American Water Resources Association 40(2):503-522.
    """
    d = np.abs(q.diff(dim="time")).resample(time=freq)
    mq = q.resample(time=freq)
    out = d.sum(dim="time") / mq.sum(dim="time")
    out.attrs["units"] = ""
    return out


@declare_units(snd="[length]")
def snd_max_doy(snd: xarray.DataArray, freq: str = "AS-JUL") -> xarray.DataArray:
    """Maximum snow depth day of year.

    Day of year when surface snow reaches its peak value. If snow depth is 0 over entire period, return NaN.

    Parameters
    ----------
    snd : xarray.DataArray
      Surface snow depth.
    freq : str
      Resampling frequency.

    Returns
    -------
    xarray.DataArray
      The day of year at which snow depth reaches its maximum value.
    """
    from xclim.core.missing import at_least_n_valid

    # Identify periods where there is at least one non-null value for snow depth
    valid = at_least_n_valid(snd.where(snd > 0), n=1, freq=freq)

    # Compute doymax. Will return first time step if all snow depths are 0.
    out = generic.select_resample_op(snd, op=generic.doymax, freq=freq)
    out.attrs["units"] = ""

    # Mask arrays that miss at least one non-null snd.
    return out.where(~valid)
