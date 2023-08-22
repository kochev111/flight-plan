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
    pattern = models.ImageField(upload_to='patterns')

    def __init__(self, inputs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.final = inputs.get("your_final",'')
        self.base = inputs.get("your_base",'')
        self.downwind = inputs.get("your_downwind",'')
        self.initial = inputs.get("your_initial",'')
        self.drop = inputs.get("your_drop",'')
        self.vspeed = inputs.get("your_vertical_speed",'')
        self.glider = inputs.get("your_glide_ratio",'')
        self.swoop = inputs.get("your_swoop",'')
        self.landing_dir = inputs.get("your_landing_direction", None)
        self.pattern_dir = inputs.get("your_pattern_direction",0)
        self.comment = inputs.get("your_comment", '')
        self.pattern = "render/langar_map.jpg"
        self.prepare_pattern()

    def prepare_pattern(self):
        inputs = {'altitudes_ft': [self.final, self.base, self.downwind, self.initial],
                  'drop_in_turn_ft': self.drop, 'vertical_speed_mph': self.vspeed,
                  'glide_ratio': self.glider, 'swoop_length_m': self.swoop,
                  'landing_dir_deg': self.landing_dir, 'hand_pattern': self.pattern_dir,
                  'comment': self.comment}
        P = Pattern(**inputs)
        self.pattern = P.render()

    def get_pattern(self):
        return self.pattern
