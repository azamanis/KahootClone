# from django.shortcuts import render, redirect
# from django.views.generic.base import TemplateView

from .forms import SignUpForm

from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth import login


class SignupView(SuccessMessageMixin, CreateView):
    # Author: Pablo Cuesta Sierra
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')
    form_class = SignUpForm
    success_message = "Your profile was created successfully"

    def form_valid(self, form):
        valid = super().form_valid(form)
        login(self.request, self.object)
        return valid


# class SignupView(TemplateView):
#     '''
#     Signup view
#     '''
#     # Author: Pablo Cuesta Sierra
#     form_class = SignUpForm
#     template_name = 'registration/signup.html'

#     def get(self, request, *args, **kwargs):
#         # Author: Pablo Cuesta Sierra
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

#     def post(self, request, *args, **kwargs):
#         # Author: Pablo Cuesta Sierra
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('home')
#         return render(request, self.template_name, {'form': form})
