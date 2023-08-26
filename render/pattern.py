import math
from PIL import Image, ImageDraw, ImageFont
from .forecast import Forecast
import datetime as dt
import time


class Pattern:
    def __init__(self, altitudes_ft=[], landing_dir_deg=None, drop_in_turn_ft=0, vertical_speed_mph=0,
                 glide_ratio=0, swoop_length_m=0, hand_pattern=0, comment=''):
        self.altitudes_ft = altitudes_ft
        if len(altitudes_ft) not in (3, 4):
            raise Exception("3 or 4 altitudes must be specified for the pattern")
        self.altitudes_m = [x / 3.28084 for x in self.altitudes_ft]
        # altitudes input in feet !
        # landing direction degrees given in runway convention, i.e. if winds are from 220, land at 220 into wind
        self.landing_dir_deg = landing_dir_deg
        # convert altitude loss quoted as a total to incremental over normal flight
        # drop in turn should be quoted as total altitude loss over a full 10-second flight cycle
        self.drop_in_turn_ft = drop_in_turn_ft
        self.incremental_drop_in_turn_ft = drop_in_turn_ft - 10 / 3600 * vertical_speed_mph * 5280
        self.incremental_drop_in_turn_m = self.incremental_drop_in_turn_ft / 3.28084
        self.vertical_speed_mph = vertical_speed_mph
        self.vertical_speed_kmh = self.vertical_speed_mph * 1.60934
        self.glide_ratio = glide_ratio
        self.swoop_length_m = swoop_length_m
        self.pattern_turn = 90 * int(hand_pattern)  # 1 if left, -1 if right
        self.pattern_dir = "Left" if int(hand_pattern) == 1 else "Right"# 1 if left, -1 if right
        self.comment = comment
        self.pattern_offsets = {}
        self.forecast = Forecast()
        self.refresh()

    def refresh(self):
        self.calculate_pattern()

    def calculate_pattern(self):
        altitudes_m = self.altitudes_m
        winds = self.forecast.get_forecast(altitudes_m)
        #     set landing direction into wind if not specified
        if self.landing_dir_deg is None:
            self.landing_dir_deg = winds[0][1]
        # convert wind and canopy track into radial vectors; quoted in wind convention (e.g. 90 is easterly)

        # work backwards from target
        final_time_hrs = (altitudes_m[0] - self.incremental_drop_in_turn_m) / 1000 / self.vertical_speed_kmh
        final_track_rad = (final_time_hrs * self.vertical_speed_kmh * self.glide_ratio * 1000
                           + self.swoop_length_m,
                           self.landing_dir_deg - 180)  # landing direction converted from runway convention
        final_drift_rad = (final_time_hrs * winds[0][0] * 1000, winds[0][1])
        final_offset = self.add_vectors(final_drift_rad, final_track_rad)

        base_time_hrs = (altitudes_m[1] - altitudes_m[0] - self.incremental_drop_in_turn_m) / 1000 / self.vertical_speed_kmh
        base_track_rad = (base_time_hrs * self.vertical_speed_kmh * self.glide_ratio * 1000,
                          self.landing_dir_deg - 180 + self.pattern_turn)
        base_drift_rad = (base_time_hrs * winds[1][0] * 1000, winds[1][1])
        base_offset = self.add_vectors(base_drift_rad, base_track_rad)

        downwind_time_hrs = (altitudes_m[2] - altitudes_m[1] - self.incremental_drop_in_turn_m) / 1000 / \
                            self.vertical_speed_kmh
        downwind_track_rad = (downwind_time_hrs * self.vertical_speed_kmh * self.glide_ratio * 1000,
                              self.landing_dir_deg - 180 + 2 * self.pattern_turn)
        downwind_drift_rad = (downwind_time_hrs * winds[2][0] * 1000, winds[2][1])
        downwind_offset = self.add_vectors(downwind_drift_rad, downwind_track_rad)

        self.pattern_offsets = {'final': final_offset,
                                'base': base_offset,
                                'downwind': downwind_offset,
                                }

        if len(altitudes_m) == 4:
            initial_time_hrs = (altitudes_m[3] - altitudes_m[2] - self.incremental_drop_in_turn_m) / 1000 / (
                self.vertical_speed_kmh)
            initial_track_rad = (downwind_time_hrs * self.vertical_speed_kmh * self.glide_ratio * 1000,
                                 self.landing_dir_deg - 180 + 3 * self.pattern_turn)
            initial_drift_rad = (initial_time_hrs * winds[3][0] * 1000, winds[3][1])
            initial_offset = self.add_vectors(initial_drift_rad, initial_track_rad)

            self.pattern_offsets['initial'] = initial_offset

    def get_pattern(self):
        return self.pattern_offsets

    def add_vectors(self, drift_rad, track_rad):
        # convert vectors to cartesian coordinates and add
        # take into account that degrees are measured from the eastern direction counter-clockwise,
        # but winds are measured from the north clockwise -> transform x:90-x
        drift_cart = (math.cos(math.radians(90 - drift_rad[1])) * drift_rad[0],
                      math.sin(math.radians(90 - drift_rad[1])) * drift_rad[0])
        track_cart = (math.cos(math.radians(90 - track_rad[1])) * track_rad[0],
                      math.sin(math.radians(90 - track_rad[1])) * track_rad[0])
        offset = (drift_cart[0] + track_cart[0], drift_cart[1] + track_cart[1])
        return offset

    def render(self):
        PLA = Image.open("render/static/render/langar_map.jpg")
        points = self.pattern_offsets
        draw = ImageDraw.Draw(PLA)
        s = PLA.size
        # draw a line matching the map's scale: 200m in this case (to be adjusted for other maps)
        draw.line((2136, 1690) + (2424, 1690), width=3, fill="white")
        draw.line((2424, 1402) + (2424, 1690), width=3, fill="white")
        scale = (2424 - 2136) / 200
        target = tuple(x / 2 for x in s)
        # fine tune the target
        target = target[0] + 20, target[1] - 30

        # flip y-direction because image is measured top-down, while carteisan y-coordinates go bottom-up
        final_setup = (target[0] + points['final'][0] * scale, target[1] - points['final'][1] * scale)
        base_setup = (final_setup[0] + points['base'][0] * scale, final_setup[1] - points['base'][1] * scale)
        downwind_setup = (base_setup[0] + points['downwind'][0] * scale, base_setup[1] -
                          points['downwind'][1] * scale)
        initial_setup = (downwind_setup[0] + points['initial'][0] * scale, downwind_setup[1] -
                         points['initial'][1] * scale)
        draw.line(target + final_setup, width=3, fill="white")
        draw.line(final_setup + base_setup, width=3, fill="white")
        draw.line(base_setup + downwind_setup, width=3, fill="white")
        draw.line(downwind_setup + initial_setup, width=3, fill="white")
        font = ImageFont.truetype("render/static/render/Arial.ttf", 30)
        text = self.make_text()
        draw.text((50, 200), text, (255, 255, 255), font=font)

        # PLA.save("flight_plan.png")
        # PLA.show()
        return PLA

    def make_text(self):
        text = "DISCLAIMER: FLIGHT PLAN IS FOR ILLUSTRATION PURPOSES ONLY\n"
        text += "Winds:\n"
        alts = self.altitudes_ft
        winds = self.forecast.get_forecast(self.altitudes_m)
        text += "Altitude ft        " + str(alts[0]) + "   " + str(alts[1]) + "   " + str(alts[2]) + "\n"
        text += "Speed kmh      " + str(round(winds[0][0])) + "     " + str(round(winds[1][0])) + "     " \
                + str(round(winds[2][0])) + "\n"
        text += "Direction deg  " + str(round(winds[0][1])) + "   " + str(round(winds[1][1])) + "   " \
                + str(round(winds[2][1])) + "\n"
        text += "\nFlight plan:\n"
        heading = self.landing_dir_deg
        turn = 90 if self.pattern_turn in ("L", "l") else -90
        text += "Altitude ft        " + str(alts[0]) + "   " + str(alts[1]) + "   " + str(alts[2]) + "\n"
        text += "Heading deg   " + str(round(heading)) + "    " + str(round((heading - turn) % 360)) \
                + "    " + str(round((heading - 2 * turn) % 360)) + "\n"
        text += "\nAssumptions:\n"
        text += "Height loss in 90 turn ft: " + str(self.drop_in_turn_ft) + "\n"
        text += "Vertical speed mph: " + str(self.vertical_speed_mph) + "\n"
        text += "Glide ratio: " + str(self.glide_ratio) + "\n"
        text += "Pattern direction: " + str(self.pattern_dir) + "\n"
        text += "Landing heading: " + str(round(self.landing_dir_deg)) + "\n"
        text += "Swoop length m: " + str(self.swoop_length_m) + "\n"
        text += "Comment: " + str(self.comment) + "\n"

        text += "\n"
        text += "Generated: " + time.strftime("%Y-%m-%d %H:%M:%S %Z, time offset: %z", time.localtime()) + "\n"
        text += "Based on open-meteo weather forecast 30min ahead\n"

        return text

#
# if __name__ == '__main__':
#     inputs = {'altitudes_ft': [400, 800, 1200, 1600], 'drop_in_turn_ft': 70, 'vertical_speed_mph': 22,
#               'glide_ratio': 2.35, 'hand_pattern': 'L', 'swoop_length_m': 5}
#     # 'landing_dir_deg' : 90
#     P = pattern(**inputs)
#     P.render()
