from pkg_resources import get_distribution

distribution = get_distribution('igwtools')
__version__ = distribution.version
