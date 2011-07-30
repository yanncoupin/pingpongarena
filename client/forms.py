# -*- coding: utf8 -*-

from django import forms
from client.models import Player

from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from itertools import chain

class PushButtonMultipleChoice(forms.CheckboxSelectMultiple):

    def __init__(self, attrs={}):
        forms.CheckboxSelectMultiple.__init__(self, attrs=attrs)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        id = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<div>']
        # Normalize to strings
        str_values = ([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                id=' id="%s_%s"' % (attrs['id'], i)
                for_id=' for="%s_%s"' % (attrs['id'], i)

            option_value = force_unicode(option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<input%s type="checkbox" name="%s" value="%s"%s><label%s>%s</label>' % (id, name, option_value, option_value in str_values and ' checked="checked"' or '', for_id, option_label))
        output.append(u'</div>')
        return mark_safe(u'\n'.join(output))

class PushButtonRadio(forms.Select):

    def render(self, name, value, attrs={}):
        options = []
        counter = 0
        for (v, l) in self.choices:
            v = force_unicode(v)
            id = '%s_%0u' % (name, counter)
            options.append('<input type="radio" name="%s" value="%s" id="%s"%s><label for="%s">%s</label>' % (
                        name, v, id, v == value and ' checked="checked"' or '', id, l))
            counter += 1
        return mark_safe('<div>%s</div>' % "\n".join(options))

class NewGameForm(forms.Form):
    team_a = forms.ModelMultipleChoiceField(queryset=Player.objects.all().order_by('name'), widget=PushButtonMultipleChoice)
    team_b = forms.ModelMultipleChoiceField(queryset=Player.objects.all().order_by('name'), widget=PushButtonMultipleChoice)
    base = forms.TypedChoiceField(choices=((11, '11'), (21, '21')), coerce=int, empty_value=0, initial=21, widget=PushButtonRadio)
    score_a = forms.IntegerField(min_value=0)
    score_b = forms.IntegerField(min_value=0)

    def clean(self):
        cleaned_data = self.cleaned_data
        team_a  = cleaned_data.get('team_a')
        team_b  = cleaned_data.get('team_b')
        base    = cleaned_data.get('base')
        score_a = cleaned_data.get('score_a')
        score_b = cleaned_data.get('score_b')

        if team_a is None or team_b is None:
            raise forms.ValidationError(u'Seuls les matchs en simple ou en double sont autorisés')
        if len(team_a) != len(team_b) or len(team_a) not in (1,2):
            raise forms.ValidationError(u'Seuls les matchs en simple ou en double sont autorisés')
        if len(set(team_a).intersection(set(team_b))) != 0:
            raise forms.ValidationError(u'Un même joueur ne peut être dans les deux camps !')

        #if (score_a <= base and score_b <= base and (base not in (score_a, score_b) or abs(score_a - score_b) < 2)) or (score_a - score_b not in (-2, 2)):
        #    raise forms.ValidationError('Score invalide !')
        if score_a <= base and score_b <= base and base not in (score_a, score_b):
            raise forms.ValidationError('Score invalide !')
        if score_a <= base and score_b <= base and abs(score_a - score_b) < 2:
            raise forms.ValidationError('Score invalide !')
        if (score_a > base or score_b > base) and score_a - score_b not in (-2, 2):
            raise forms.ValidationError('Score invalide !')

        return cleaned_data
