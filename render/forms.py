from django import forms

CHOICES = [
    (1, 'Left'),
    (-1, 'Right'),
]
class InputForm(forms.Form):
    your_final = forms.IntegerField(label="Final approach height, ft", min_value=200,
                                             max_value=2000, initial=400, step_size=1)
    your_base = forms.IntegerField(label="Base leg height, ft", min_value=200,
                                             max_value=2000, initial=800, step_size=1)
    your_downwind = forms.IntegerField(label="Downwind leg height, ft", min_value=200,
                                             max_value=2000, initial=1200, step_size=1)
    your_initial = forms.IntegerField(label="Initial setup height, ft", min_value=200,
                                             max_value=2500, initial=1600, step_size=1)
    your_drop = forms.IntegerField(label="Height loss in a plain 90-degree turn (10s flight cycle), ft",
                                      min_value=5, max_value=1000, initial=240)
    your_final_drop = forms.IntegerField(label="Height loss in your final turn (10s flight cycle), ft",
                                      min_value=5, max_value=1500, initial=240)

    your_vertical_speed = forms.IntegerField(label="Vertical speed in normal flight, mph", min_value=1,
                                             max_value=100, initial=15, step_size=1)
    your_glide_ratio = forms.FloatField(label="Glide Ratio", min_value=0.00,
                                        max_value=10, initial=2.75, step_size=0.01)
    your_swoop = forms.IntegerField(label="Swoop length, m", min_value=0,
                                             max_value=200, initial=0, step_size=1)
    your_landing_direction = forms.IntegerField(label="Landing heading, degrees (into wind if blank)", min_value=0,
                                             max_value=360, step_size=1, required=False)
    your_pattern_direction = forms.ChoiceField(label="Pattern Direction", widget=forms.RadioSelect, choices=CHOICES)
    your_comment = forms.CharField(label="Comment (for display only)", max_length=100, required=False)
