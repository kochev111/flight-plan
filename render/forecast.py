from urllib import request
from datetime import timezone
from datetime import datetime as datetime
import json
import numpy as np
import math

alt_fixed = [10, 80, 120, 180]
HPA = [1000, 975, 950, 925, 900, 850, 800, 700, 600, 500]


def integrate_array(Y, X, x):
    start = X[0]
    sum = 0
    for i in range(1, len(X) - 1):
        if x > X[i]:
            sum += (X[i] - X[i - 1]) * (Y[i] + Y[i - 1]) / 2
        else:
            sum += (x - X[i - 1]) * (Y[i] + Y[i - 1]) / 2
            return sum


def get_input_from_url():
    # using skydive Langar coordinates
    req = request.urlopen(
        "https://api.open-meteo.com/v1/forecast?latitude=52.8906&longitude=-0.905556&hourly=windspeed_10m,windspeed_80m,windspeed_120m,windspeed_180m,winddirection_10m,winddirection_80m,winddirection_120m,winddirection_180m,windgusts_10m,windspeed_1000hPa,windspeed_975hPa,windspeed_950hPa,windspeed_925hPa,windspeed_900hPa,windspeed_850hPa,windspeed_800hPa,windspeed_700hPa,windspeed_600hPa,windspeed_500hPa,winddirection_1000hPa,winddirection_975hPa,winddirection_950hPa,winddirection_925hPa,winddirection_900hPa,winddirection_850hPa,winddirection_800hPa,winddirection_700hPa,winddirection_600hPa,winddirection_500hPa,geopotential_height_1000hPa,geopotential_height_975hPa,geopotential_height_950hPa,geopotential_height_925hPa,geopotential_height_900hPa,geopotential_height_850hPa,geopotential_height_800hPa,geopotential_height_700hPa,geopotential_height_600hPa,geopotential_height_500hPa&timezone=GMT&forecast_days=1")
    j = json.loads(req.read())
    return j


class Forecast:
    def __init__(self):
        self.input = {}
        self.time_grid = ''
        self.forecast = ''
        self.forecast_altitude_m = ''
        self.forecast_windspeed_kmh = ''
        self.forecast_winddirection_deg = ''
        self.refresh()

    def refresh(self):
        self.input = get_input_from_url()
        self.time_grid = [datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in self.input['hourly']['time']]
        self.forecast = self.build_forecast()

    def get_forecast(self, altitudes):
        """ input : array of turn altitudes in meters e.g. [100, 200, 300, 400]
            returns array of forecast tuples (speed kmh, direction deg) integrated over the altitudes"""
        ret = []
        alts = [0] + altitudes
        s_integrated = [integrate_array(self.forecast_windspeed_kmh, self.forecast_altitude_m, x) for x in alts]
        """convert angle to cartesian pair"""
        d_sin = [math.sin(math.radians(x)) for x in self.forecast_winddirection_deg]
        d_cos = [math.cos(math.radians(x)) for x in self.forecast_winddirection_deg]
        d_integrated_s = [integrate_array(d_sin, self.forecast_altitude_m, x) for x in alts]
        d_integrated_c = [integrate_array(d_cos, self.forecast_altitude_m, x) for x in alts]
        for i in range(0, len(alts) - 1):
            speed = (s_integrated[i + 1] - s_integrated[i]) / (alts[i + 1] - alts[i])
            direction = math.degrees(math.atan2((d_integrated_s[i + 1] - d_integrated_s[i]) / (alts[i + 1] - alts[i]),
                                                (d_integrated_c[i + 1] - d_integrated_c[i]) / (
                                                            alts[i + 1] - alts[i]))) % 360
            ret += [(speed, direction)]
        return ret

    def build_forecast(self):
        self.now = datetime.now(tz=timezone.utc)
        self.t = np.interp(self.now.timestamp(), [t.timestamp() for t in self.time_grid],
                           np.arange(0, len(self.time_grid)))
        return self.interpolate_forecast()

    def interpolate_forecast(self):
        winds_fixed = [self.interpolate_array(self.input['hourly']['windspeed_' + str(h) + 'm']) for h in alt_fixed]
        windd_fixed = [self.interpolate_array(self.input['hourly']['winddirection_' + str(h) + 'm']) for h in alt_fixed]
        alt_from_hpa = [self.interpolate_array(self.input['hourly']['geopotential_height_' + str(h) + 'hPa']) for h in
                        HPA]
        winds_from_hpa = [self.interpolate_array(self.input['hourly']['windspeed_' + str(h) + 'hPa']) for h in HPA]
        windd_from_hpa = [self.interpolate_array(self.input['hourly']['winddirection_' + str(h) + 'hPa']) for h in HPA]
        alt = [x - self.input['elevation'] for x in alt_fixed + alt_from_hpa]
        winds = winds_fixed + winds_from_hpa
        windd = windd_fixed + windd_from_hpa

        """ adjust altitudes (above sea level) for elevation at target """
        self.forecast_altitude_m = sorted(alt)
        self.forecast_windspeed_kmh = [w for _, w in sorted(zip(alt, winds))]
        self.forecast_winddirection_deg = [w for _, w in sorted(zip(alt, windd))]
        return {'altitude': self.forecast_altitude_m, 'wind_speed': self.forecast_windspeed_kmh,
                'wind_direction': self.forecast_winddirection_deg}

    def interpolate_array(self, array):
        return np.interp(self.t, np.arange(0, len(self.time_grid)), array)
