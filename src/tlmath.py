import numpy as np

def calculate_inflow_rate(z_min, z_max, inflow_amounts):
    #z_min, z_max = int(z_arr.min()), int(z_arr.max() ) +1
    q_in = np.zeros(z_max - z_min + 1)

    heights = list(inflow_amounts.keys())

    for height in heights:
        _z_min = height[0]
        _z_max = height[1]
        if _z_min < z_min:
            _z_min = z_min
        if _z_max > z_max:
            _z_max = z_max

        _amount = inflow_amounts[height]
        try:
            _rate = _amount / (_z_max - _z_min)
        except:
            _rate = 0.
        for _z in range(_z_min, _z_max):
            q_in[_z - z_min] += _rate

    return q_in