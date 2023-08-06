from mako.runtime import UNDEFINED
from pkg_resources import DistributionNotFound
from mock import Mock
from versiontag import distribution

def test_returns_version():
    context = Mock()
    
    get_distribution = Mock()
    get_distribution('bloom').version = '1.2.3.4'
    
    version = distribution(context, 'bloom', _get_distribution=get_distribution)
    
    assert (('bloom',), {}) == get_distribution.call_args
    assert '1.2.3.4' == version

def test_no_dist_UNDEFINED():
    def no_such_dist(*args, **kwargs):
        raise DistributionNotFound
    
    context = Mock()
    
    get_distribution = Mock()
    get_distribution.side_effect = no_such_dist
    
    version = distribution(context, 'flooble', _get_distribution=get_distribution)
    
    assert (('flooble',), {}) == get_distribution.call_args
    assert version == UNDEFINED
