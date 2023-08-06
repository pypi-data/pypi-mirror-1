from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

class UserForm(auth_forms.UserChangeForm):
    class Meta(auth_forms.UserChangeForm.Meta):
        fields = ('username', 'email')

class UserCreationForm(auth_forms.UserCreationForm):
    class Meta(auth_forms.UserCreationForm.Meta):
        fields = ('username', 'email')

class SetPasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ('username')

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.instance.set_password(self.cleaned_data["password1"])
        if commit:
            self.instance.save()
        return self.instance

