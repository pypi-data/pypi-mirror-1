"""A Mako-compatible module for writing out distribution versions from
``pkg_resources``.

.. highlight:: mako

To use the functions from this module in your Mako pages, import it into
a namespace ::

   <%namespace name="v" module="versiontag"/>
"""

import mako.runtime
import pkg_resources

__all__ = ['distribution']


def distribution(context, distribution_spec, _get_distribution=pkg_resources.get_distribution):
    """Returns the distribution version of ``distribution_spec``.
    
    For example, to write the version of this library out to the page ::
    
        ${v.distribution('mako-version-tag')}
    
    Missing distributions are replaced with the Mako ``UNDEFINED`` constant.
    """
    try:
        dist = _get_distribution(distribution_spec)
        return dist.version
    except (ValueError, pkg_resources.DistributionNotFound):
        return mako.runtime.UNDEFINED
