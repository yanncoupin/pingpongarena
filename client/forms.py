# -*- coding: utf8 -*-

from django import forms
from client.models import Player

class NewGameForm(forms.Form):
    team_a = forms.ModelMultipleChoiceField(queryset=Player.objects.all().order_by('name'), widget=forms.CheckboxSelectMultiple)
    team_b = forms.ModelMultipleChoiceField(queryset=Player.objects.all().order_by('name'), widget=forms.CheckboxSelectMultiple)
    base = forms.TypedChoiceField(choices=((11, 11), (21, 21)), coerce=int, widget=forms.RadioSelect, initial=21)
    score_a = forms.IntegerField(min_value=0)
    score_b = forms.IntegerField(min_value=0)

    def clean(self):
        cleaned_data = self.cleaned_data
        team_a  = cleaned_data.get('team_a')
        team_b  = cleaned_data.get('team_b')
        base    = cleaned_data.get('base')
        score_a = cleaned_data.get('score_a')
        score_b = cleaned_data.get('score_b')

        if len(team_a) != len(team_b) or len(team_a) not in (1,2):
            raise forms.ValidationError('Seuls les matchs en simple ou en double sont autorisés')
        if len(set(team_a).intersection(set(team_b))) != 0:
            raise forms.ValidationError('Un même joueur ne peut être dans les deux camps !')

        #if (score_a <= base and score_b <= base and (base not in (score_a, score_b) or abs(score_a - score_b) < 2)) or (score_a - score_b not in (-2, 2)):
        #    raise forms.ValidationError('Score invalide !')
        if score_a <= base and score_b <= base and base not in (score_a, score_b):
            raise forms.ValidationError('Score invalide !')
        if score_a <= base and score_b <= base and abs(score_a - score_b) < 2:
            raise forms.ValidationError('Score invalide !')
        if (score_a > base or score_b > base) and score_a - score_b not in (-2, 2):
            raise forms.ValidationError('Score invalide !')

        return cleaned_data
