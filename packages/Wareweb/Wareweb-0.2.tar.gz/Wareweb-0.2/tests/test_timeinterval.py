from wareweb.timeinterval import *

def test_encode_decode():
    for time, s_in, s_out in [(1000, '16m40s', '16m40s'),
                    (5, '5s', '5s'),
                    (874805, '10d3h5s', '1w3d3h5s')]:
        assert time_decode(s_in) == time
        assert time_encode(time) == s_out
