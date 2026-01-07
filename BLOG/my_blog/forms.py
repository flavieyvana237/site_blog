from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(label="Prénom", max_length=30)
    last_name = forms.CharField(label="Nom", max_length=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            })

        # 🔁 ORDRE DES CHAMPS
        self.fields = {
            "first_name": self.fields["first_name"],
            "last_name": self.fields["last_name"],
            "email": self.fields["email"],
            "username": self.fields["username"],
            "password1": self.fields["password1"],
            "password2": self.fields["password2"],
        }

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user
