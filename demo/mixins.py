from django.views.generic.edit import FormMixin, ModelFormMixin

class ReadOnlyModelFormMixin(ModelFormMixin):

    def get_form(self, form_class=None):

        form = super(ReadOnlyModelFormMixin, self).get_form()

        for field in form.fields:
            # Set html attributes as needed for all fields
            form.fields[field].widget.attrs['readonly'] = 'readonly'
            form.fields[field].widget.attrs['disabled'] = 'disabled'

        return form

    def form_valid(self, form):
        """
        Called when form is submitted and form.is_valid()
        """
        return self.form_invalid(form)