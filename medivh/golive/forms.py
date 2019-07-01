from django import forms
from golive.models import Service, ECS, SLB
from django.contrib.admin.widgets import FilteredSelectMultiple

class ServiceForm(forms.ModelForm):
    ecses = forms.ModelMultipleChoiceField(
        queryset=ECS.objects.all(), 
        widget=FilteredSelectMultiple("ecs", is_stacked=False)
    )
    slbs = forms.ModelMultipleChoiceField(
        queryset=SLB.objects.all(), 
        widget=FilteredSelectMultiple("slb", is_stacked=False),
        required = False
    )


class ServiceExecutionInfoForm(forms.ModelForm):
    ecses = forms.ModelMultipleChoiceField(
        queryset=ECS.objects.all(),
        widget=FilteredSelectMultiple("ecs", is_stacked=False)
    )
