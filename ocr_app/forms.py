from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Upload, Output


class RegisterForm(forms.ModelForm):
    # username = forms.CharField(max_length=60)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    # Contact = forms.IntegerField()

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    # remember_me = forms.BooleanField()

    class Meta:
        model = User
        fields = ['email', 'password', 'Contact']

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    remember_me = forms.BooleanField()

    class Meta:
        model = User
        fields = ['email', 'password']

class OutputForm(forms.ModelForm):
    class Meta:
        model = Output
        fields = '__all__'

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active or not user.is_validated:
            raise forms.ValidationError('There was a problem with your login.', code='invalid_login')


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['FileName', 'File', 'operation']
