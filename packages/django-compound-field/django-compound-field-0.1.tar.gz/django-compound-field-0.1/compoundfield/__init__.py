try:
    from field import CompoundField
except ImportError:             # that's ugly but it probably means that we are being run from inside the unittests and django settings are not there yet.
    pass
