import fissile
import pytest

fooval1, fooval2 = 0, 0


@fissile.func(name='foo', tag='blah', method='get')
def foo_read(pval1=None, pval2=None):
    return [fooval1, fooval2]


@fissile.func(name='foo', tag='blah', method='post')
def foo_write(pval1=None, pval2=None):
    global fooval1
    global fooval2
    if pval1:
        fooval1 = pval1
    if pval2:
        fooval2 = pval2
    return [fooval1, fooval2]


# show that the result is the same whether it's in front-end or no-split mode
#
# note: this might require some magic...maybe...think on it

# show that a call in backend mode produces the expected response

class TestDecorator(object):

    def test_it(self):
        assert(False)
