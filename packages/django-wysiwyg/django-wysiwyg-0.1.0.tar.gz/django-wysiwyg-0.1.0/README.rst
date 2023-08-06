DJANGO WYSIWYG
==================

A Django application for easily converting HTML <textarea>s into rich HTML editors that meet US Government 508/WAC standards. This application has been demonstrated to work just fine with django-uni-form (http://github.com/pydanny/django-uni-form).

Currently this works as a template tag. We did it this way because control of how editing works is arguably a template issue (i.e. presentation) and not a forms/model issue (i.e. control).

At the moment we are using YUI's editor because of familiarity and because it meant we . We considered other options such as TinyMCE, FCKeditor, various jquery tools and other tools.

If you want to contribute to django-wysiwyg, please do so from the repository at http://github.com/pydanny/django-wysiwyg.

Installation
~~~~~~~~~~~~~~~~

Via pip::

  easy_install django-wysiwyg

Via easy_setup::

  pip install django-wysiwyg
    
Configuration
~~~~~~~~~~~~~~

Add `'django_wysiyg'` to your `INSTALLED_APPS` in `settings.py`::

    INSTALLED_APPS = (
        ...
        'django_wysiyg',
    )

Usage
~~~~~~

Within your pages
-----------------

::

    {% load wysiwyg %}

    {% wysiwyg_setup %}

    <textarea id="foo">

    </textarea>

    {% wysiwyg_editor "my_text_area_id" %}

Within Django Admin
-------------------

Copy `templates/admin/change_form.html` to your template root for the areas
you want to enable rich editing - e.g. `templates/admin/myapp/mymodel.html`
- and, if your HTML object is not named "body" adjust the id passed to the
`wysiwyg_editor` tag (note that Django admin will prefix your field names
with `id_`).

Handling Content
~~~~~~~~~~~~~~~~

Cleaning HTML
-------------

django_wyswyg.clean_html will be exported if you have either html5lib
(http://code.google.com/p/html5lib/) or pytidylib installed. Both should
install with pip or easy_install, although the later will require having the
htmltidy C library installed.

Using clean_html in views is simple::

    data = django_wyswyg.clean_html(data)

To display raw HTML
-------------------

In your templates::

    {% autoescape off %}
        {{ content }}
    {% endautoescape %}

or::

    {{ content|safe }}

*This should not be used without careful consideration if your content comes
from untrusted users*

`clean_html` does not protect against security problems; `sanitize_html`
attempts to do so but is only available with html5lib (tidylib has no
equivalent mode) and should currently be considered experimental.