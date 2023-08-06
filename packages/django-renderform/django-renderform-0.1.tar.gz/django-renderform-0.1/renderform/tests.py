from django.test import TestCase
from django import forms
from django.template import Context
from django.template.loader import render_to_string, get_template_from_string


class ContactForm(forms.Form):
    email = forms.EmailField(label="email address")
    home_page = forms.URLField(required=False)
    message = forms.CharField(widget=forms.Textarea, required=False)
    remember_me = forms.BooleanField(required=False)
    honeypot = forms.CharField(
        widget=forms.HiddenInput, required=False, help_text="Leave blank!"
    )
    
    def clean(self):
        if self.cleaned_data['honeypot']:
            raise forms.ValidationError("Spam detected!")
        return self.cleaned_data

class RenderTest(TestCase):
    form_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_form form %}
           {% endspaceless %}"""
    )
    form_as_p_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_form form "p" %}
           {% endspaceless %}"""
    )
    field_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_field field %}
           {% endspaceless %}"""
    )
    field_as_p_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_field field "p" %}
           {% endspaceless %}"""
    )
    field_classes_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_field field "li" "highlight,row" %}
           {% endspaceless %}"""
    )
    help_text_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_help_text field %}
           {% endspaceless %}"""
    )
    help_text_classes_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_help_text field.help_text field.name %}
           {% endspaceless %}"""
    )
    custom_help_text_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_help_text "Whatever text I want!" %}
           {% endspaceless %}"""
    )
    label_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_label field %}
           {% endspaceless %}"""
    )
    custom_label_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_label field label %}
           {% endspaceless %}"""
    )
    label_classes_template = get_template_from_string(
        """{% load forms %}{% spaceless %}
           {% show_label field field.label "not-required" %}
           {% endspaceless %}"""
    )
    
    def setUp(self):
        self.contact_form = ContactForm()
        self.contact_form_no_id = ContactForm(auto_id=None)
        self.contact_form_field_errors = ContactForm({})
        self.contact_form_non_field_errors = ContactForm(
            {'email': 'spam@example.com', 'honeypot': 'enh4nce y0ur djang0'}
        )
    
    def test_show_form(self):
        form = self.contact_form
        output = self.form_template.render(Context({'form': form}))
        self.failUnlessEqual(output, u'<div class="field email required"><label for="id_email">email address</label><input type="text" name="email" id="id_email" /></div><div class="field home_page"><label for="id_home_page">Home page</label><input type="text" name="home_page" id="id_home_page" /></div><div class="field message"><label for="id_message">Message</label><textarea id="id_message" rows="10" cols="40" name="message"></textarea></div><div class="field remember_me"><input type="checkbox" name="remember_me" id="id_remember_me" /><label for="id_remember_me">Remember me</label></div><div class="field honeypot hidden"><input type="hidden" name="honeypot" id="id_honeypot" /></div>')
    
    def test_show_form_as_p(self):
        form = self.contact_form
        output = self.form_as_p_template.render(Context({'form': form}))
        self.failUnlessEqual(output, u'<p class="field email required"><label for="id_email">email address</label><input type="text" name="email" id="id_email" /></p><p class="field home_page"><label for="id_home_page">Home page</label><input type="text" name="home_page" id="id_home_page" /></p><p class="field message"><label for="id_message">Message</label><textarea id="id_message" rows="10" cols="40" name="message"></textarea></p><p class="field remember_me"><input type="checkbox" name="remember_me" id="id_remember_me" /><label for="id_remember_me">Remember me</label></p><p class="field honeypot hidden"><input type="hidden" name="honeypot" id="id_honeypot" /></p>')
    
    def test_show_form_field_errors(self):
        form = self.contact_form_field_errors
        output = self.form_template.render(Context({'form': form}))
        self.failUnlessEqual(output, u'<div class="field email required errors"><ul class="errorlist"><li>This field is required.</li></ul><label for="id_email">email address</label><input type="text" name="email" id="id_email" /></div><div class="field home_page"><label for="id_home_page">Home page</label><input type="text" name="home_page" id="id_home_page" /></div><div class="field message"><label for="id_message">Message</label><textarea id="id_message" rows="10" cols="40" name="message"></textarea></div><div class="field remember_me"><input type="checkbox" name="remember_me" id="id_remember_me" /><label for="id_remember_me">Remember me</label></div><div class="field honeypot hidden"><input type="hidden" name="honeypot" id="id_honeypot" /></div>')
    
    def test_show_form_non_field_errors(self):
        form = self.contact_form_non_field_errors
        form.errors
        output = self.form_template.render(Context({'form': form}))
        self.failUnlessEqual(output, u'<ul class="errorlist"><li>Spam detected!</li></ul><div class="field email required"><label for="id_email">email address</label><input type="text" name="email" value="spam@example.com" id="id_email" /></div><div class="field home_page"><label for="id_home_page">Home page</label><input type="text" name="home_page" id="id_home_page" /></div><div class="field message"><label for="id_message">Message</label><textarea id="id_message" rows="10" cols="40" name="message"></textarea></div><div class="field remember_me"><input type="checkbox" name="remember_me" id="id_remember_me" /><label for="id_remember_me">Remember me</label></div><div class="field honeypot hidden"><input type="hidden" name="honeypot" value="enh4nce y0ur djang0" id="id_honeypot" /></div>')
    
    def test_show_field(self):
        field = self.contact_form['email']
        output = self.field_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<div class="field email required"><label for="id_email">email address</label><input type="text" name="email" id="id_email" /></div>')
    
    def test_show_field_checkbox(self):
        field = self.contact_form['remember_me']
        output = self.field_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<div class="field remember_me"><input type="checkbox" name="remember_me" id="id_remember_me" /><label for="id_remember_me">Remember me</label></div>')
    
    def test_show_field_as_p(self):
        field = self.contact_form['home_page']
        output = self.field_as_p_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<p class="field home_page"><label for="id_home_page">Home page</label><input type="text" name="home_page" id="id_home_page" /></p>')
    
    def test_show_field_classes(self):
        field = self.contact_form['message']
        output = self.field_classes_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<li class="field message highlight row"><label for="id_message">Message</label><textarea id="id_message" rows="10" cols="40" name="message"></textarea></li>')

    def test_show_help_text(self):
        field = self.contact_form['honeypot']
        output = self.help_text_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<p class="help">Leave blank!</p>')
    
    def test_show_help_text_classes(self):
        field = self.contact_form['honeypot']
        output = self.help_text_classes_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<p class="help honeypot">Leave blank!</p>')
    
    def test_show_help_text_custom(self):
        field = self.contact_form['honeypot']
        output = self.custom_help_text_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<p class="help">Whatever text I want!</p>')

    def test_show_label(self):
        field = self.contact_form['remember_me']
        output = self.label_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<label for="id_remember_me">Remember me</label>')

    def test_show_label_no_id(self):
        field = self.contact_form_no_id['remember_me']
        output = self.label_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<label>Remember me</label>')

    def test_show_label_custom(self):
        field = self.contact_form['remember_me']
        output = self.custom_label_template.render(Context(
            {'field': field, 'label': "Remember my information for later"}
        ))
        self.failUnlessEqual(output, u'<label for="id_remember_me">Remember my information for later</label>')

    def test_show_label_classes(self):
        field = self.contact_form['remember_me']
        output = self.label_classes_template.render(Context({'field': field}))
        self.failUnlessEqual(output, u'<label for="id_remember_me" class="not-required">Remember me</label>')
