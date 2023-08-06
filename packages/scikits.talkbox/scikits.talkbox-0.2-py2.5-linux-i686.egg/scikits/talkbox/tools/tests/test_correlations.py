import numpy as np
from numpy.testing import TestCase, assert_array_equal, assert_array_almost_equal

from scikits.talkbox.tools.correlations import nextpow2, acorr

class TestNextpow2(TestCase):
    X = np.array([0, 1, 2, 3, 4, 6, 8, 15, 16, 17, 32, np.nan, np.infty])
    Y = np.array([0., 0, 1, 2, 2, 3, 3, 4, 4, 5, 5, np.nan, np.infty])
    def test_simple(self):
        assert nextpow2(0) == 0
        assert nextpow2(1) == 0
        assert nextpow2(2) == 1
        assert nextpow2(3) == 2
        assert nextpow2(4) == 2

    def test_vector(self):
        assert_array_equal(nextpow2(self.X), self.Y)

class _TestCorrCommon(TestCase):
    X = np.linspace(1, 11, 11)
    Y = np.array([11.0000, 32.0000, 62.0000, 100.0000, 145.0000, 196.0000,
                  252.0000, 312.0000, 375.0000, 440.0000, 506.0000, 440.0000,
                  375.0000, 312.0000, 252.0000, 196.0000, 145.0000, 100.0000,
                  62.0000, 32.0000 , 11.0000])

    Xm = np.linspace(1, 22, 22).reshape(2, 11)
    Ym = np.array([[11.,   32.,   62.,  100.,  145.,  196.,  252.,  312.,  375.,
                    440.,  506.,  440.,  375.,  312.,  252.,  196.,  145.,  100.,
                    62.,   32.,   11.],
                   [264.,   538.,   821.,  1112.,  1410.,  1714.,  2023.,  2336.,
                    2652.,  2970.,  3289.,  2970.,  2652.,  2336.,  2023.,  1714.,
                    1410.,  1112.,   821.,   538.,   264.]])

class TestAcorr(_TestCorrCommon):
    def test_simple(self):
        """Test autocorrelation for a rank 1 array."""
        a = acorr(self.X)
        assert_array_almost_equal(a, self.Y)

    def test_axis0(self):
        """Test autocorrelation along default axis."""
        a = acorr(self.Xm)
        assert_array_almost_equal(a, self.Ym)

    def test_axis1(self):
        """Test autocorrelation along axis 0."""
        a = acorr(self.Xm.T, axis=0)
        assert_array_almost_equal(a, self.Ym.T)
