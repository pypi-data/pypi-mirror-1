"""A Mako-compatible module for writing out distribution versions from
``pkg_resources``.

.. highlight:: mako

To use the functions from this module in your Mako pages, import it into
a namespace ::

   <%namespace name="v" module="versiontag"/>
"""

import pkg_resources

__all__ = ['distribution']


def distribution(context, distribution_spec, _get_distribution=pkg_resources.get_distribution):
    """Writes the distribution version of ``distribution_spec`` to ``context``.
    
    For example, to write the version of this library out to the page ::
    
        ${v.distribution('mako-version-tag')}
    
    Missing distributions are skipped, silently.
    """
    try:
        dist = _get_distribution(distribution_spec)
        context.write(dist.version)
    except pkg_resources.DistributionNotFound:
        pass
