from django import forms

CHOICES = [
    ('1', 'Left'),
    ('-1', 'Right'),
]
class InputForm(forms.Form):
    your_comment = forms.CharField(label="Comment, e.g. canopy model & size", max_length=100, required=False)
    your_drop = forms.IntegerField(label="Vertical drop in a 90-degree turn, feet",
                                      min_value="5", max_value="1000", initial="50")
    your_vertical_speed = forms.IntegerField(label="Vertical speed, mph", min_value="1",
                                             max_value="100", initial="20", step_size="1")
    your_glide_ratio = forms.FloatField(label="Glide Ratio", min_value="0.00",
                                        max_value="10", initial="2.5", step_size="0.01")
    your_pattern_direction = forms.ChoiceField(label="Pattern Direction", widget=forms.RadioSelect, choices=CHOICES)
    your_swoop = forms.IntegerField(label="Swoop length, m", min_value="0",
                                             max_value="200", initial="5", step_size="1")
    your_final = forms.IntegerField(label="Final approach height, ft", min_value="200",
                                             max_value="1000", initial="400", step_size="1")
    your_base = forms.IntegerField(label="Base leg height, ft", min_value="200",
                                             max_value="1000", initial="800", step_size="1")
    your_downwind = forms.IntegerField(label="Downwind leg height, ft", min_value="200",
                                             max_value="2000", initial="1200", step_size="1")
    your_initial = forms.IntegerField(label="Initial setup height, ft", min_value="200",
                                             max_value="2000", initial="1600", step_size="1")
    your_landing_direction = forms.IntegerField(label="Swoop length, m", min_value="0",
                                             max_value="360", step_size="1", required=False)
