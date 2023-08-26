from django.db import models
from .pattern import Pattern


class Plan(models.Model):
    final = models.IntegerField()
    base = models.IntegerField()
    downwind = models.IntegerField()
    initial = models.IntegerField()
    drop = models.IntegerField()
    final_drop = models.IntegerField()
    vertical_speed = models.IntegerField()
    glide_ratio = models.FloatField()
    swoop = models.IntegerField()
    landing_dir = models.IntegerField(null=True, blank=True)
    pattern_dir = models.IntegerField()
    comment = models.CharField(max_length=100)
    pattern = models.ImageField(upload_to='plans')

    def __init__(self, inputs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.final = inputs.get("your_final",'')
        self.base = inputs.get("your_base",'')
        self.downwind = inputs.get("your_downwind",'')
        self.initial = inputs.get("your_initial",'')
        self.drop = inputs.get("your_drop",'')
        self.final_drop = inputs.get("your_final_drop",'')
        self.vertical_speed = inputs.get("your_vertical_speed", '')
        self.glide_ratio = inputs.get("your_glide_ratio", '')
        self.swoop = inputs.get("your_swoop",'')
        self.landing_dir = inputs.get("your_landing_direction", None)
        self.pattern_dir = inputs.get("your_pattern_direction",0)
        self.comment = inputs.get("your_comment", '')
        self.pattern = "render/static/render/langar_map.jpg"

    def prepare_pattern(self):
        inputs = {'altitudes_ft': [self.final, self.base, self.downwind, self.initial],
                  'drop_in_turn_ft': self.drop, 'final_drop_in_turn_ft': self.final_drop,
                  'vertical_speed_mph': self.vertical_speed,
                  'glide_ratio': self.glide_ratio, 'swoop_length_m': self.swoop,
                  'landing_dir_deg': self.landing_dir, 'hand_pattern': self.pattern_dir,
                  'comment': self.comment}
        p = Pattern(**inputs)
        self.pattern = p.render()

    def get_pattern(self):
        return self.pattern
