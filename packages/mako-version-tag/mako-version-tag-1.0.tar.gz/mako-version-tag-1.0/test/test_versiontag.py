from pkg_resources import DistributionNotFound
from mock import Mock, Sentinel
from versiontag import distribution

def test_writes_version():
    context = Mock()
    
    get_distribution = Mock()
    get_distribution('bloom').version = '1.2.3.4'
    
    distribution(context, 'bloom', _get_distribution=get_distribution)
    
    assert (('bloom',), {}) == get_distribution.call_args
    assert (('1.2.3.4',), {}) == context.write.call_args

def test_writes_version():
    def no_such_dist(*args, **kwargs):
        raise DistributionNotFound
    
    context = Mock()
    
    get_distribution = Mock()
    get_distribution.side_effect = no_such_dist
    
    distribution(context, 'flooble', _get_distribution=get_distribution)
    
    assert (('flooble',), {}) == get_distribution.call_args
    assert 0 == context.write.call_count
