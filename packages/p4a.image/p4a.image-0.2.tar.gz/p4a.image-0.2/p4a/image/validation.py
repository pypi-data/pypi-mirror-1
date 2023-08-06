from zope.schema import interfaces as schema_ifaces
from zope.app.form import interfaces as za_form_ifaces

from p4a.image import interfaces

class ValidationView(object):

    interface = interfaces.IImage

    def __call__(self):
        """Validate the adapted context against the interface"""
        adapter = self.interface(self.context)
        errors = []
        for name in self.interface:
            field = self.interface[name]
            field.bind(adapter)
            try:
                field.validate(getattr(adapter, name))
            except schema_ifaces.ValidationError, error:
                error = za_form_ifaces.WidgetInputError(
                    name, field.title, error)
                errors.append(error)
        return errors
