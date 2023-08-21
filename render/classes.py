from django.db import models
from .pattern import Pattern

class Plan(models.Model):
    final = models.IntegerField()
    base = models.IntegerField()
    downwind = models.IntegerField()
    initial = models.IntegerField()
    drop = models.IntegerField()
    vspeed = models.IntegerField()
    glider = models.FloatField()
    swoop = models.IntegerField()
    landing_dir = models.IntegerField()
    pattern_dir = models.IntegerField()
    comment = models.CharField(max_length=100)
    pattern = models.ImageField()

    def __init__(self, inputs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.final = inputs["your_final"]
        self.base = inputs["your_base"]
        self.downwind = inputs["your_downwind"]
        self.initial = inputs["your_initial"]
        self.drop = inputs["your_drop"]
        self.vspeed = inputs["your_vertical_speed"]
        self.glider = inputs["your_glide_ratio"]
        self.swoop = inputs["your_swoop"]
        self.landing_dir = inputs.get("your_landing_direction",None)
        self.pattern_dir = inputs["your_pattern_direction"]
        self.comment = inputs.get("your_comment",'')

    def prepare_pattern(self):
        inputs = {'altitudes_ft': [self.final, self.base, self.downwind, self.initial],
                  'drop_in_turn_ft': self.drop, 'vertical_speed_mph': self.vspeed,
                  'glide_ratio': self.glider, 'swoop_length_m': self.swoop,
                  'landing_dir_deg': self.landing_dir, 'hand_pattern': self.pattern_dir,
                  'comment': self.comment}
        P = Pattern(**inputs)
        self.pattern = P.render()
