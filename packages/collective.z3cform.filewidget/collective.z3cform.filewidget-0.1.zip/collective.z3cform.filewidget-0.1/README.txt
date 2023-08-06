collective.z3cform.filewidget
=============================

This package provides a simple widget for file upload and edit. It is registered for zope.schema.interfaces.IBytes. The original file widget allows only upload and thus it is usable only with z3c.form.AddForm.

It can be used together with archetypes' FileField, however the z3c.form's applyChanges cannot handle filename and content_type properly, so please note that you have to tweak it yourself.

The aim was to override the default behavior without creating a new field as plone.namedfile does.

Usage
=====
Add the package into you buildout's egg section or your package's setup.py and rerun buildout.

In your form reassign the widget::

	from collective.z3cform.filewidget import FileFieldWidget

	class YourForm(form.EditForm):
	    fields = field.Fields(IYourForm)
	    fields['file'].widgetFactory[INPUT_MODE] = FileFieldWidget


The value returned from the widget (convertor) is either raw data of the uploaded file or a collective.z3cform.filewidget.NOCHANGE indicating that the file has not been changed.

The filename and headers are stored within the widget instance itself::

	filename = self.widgets['file'].filename
	headers = self.widgets['file'].headers

