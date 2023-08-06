# -*- coding: utf-8 -*-
r"""
>>> import os
>>> from django import forms
>>> from softwarefabrica.django.forms import extended
>>> from django.db.models import Q
>>> from softwarefabrica.django.forms.tests.models import *

>>> neruda = Author(name = 'Pablo', last_name = 'Neruda', birth_year = 1904, active = True)
>>> neruda.save()

>>> shakespeare = Author(name = 'William', last_name = 'Shakespeare', birth_year = 1564, active = True)
>>> shakespeare.save()

>>> book = Book(title = "A Midsummer Night's Dream", isbn='ABCD12', author=shakespeare, active=True)
>>> book.save()

Let's try our extended Form.

>>> class SimpleAuthorForm(extended.Form):
...     name       = forms.CharField(max_length=50)
...     last_name  = forms.CharField(max_length=50)
...     birth_year = forms.IntegerField()
...     active     = forms.BooleanField()

>>> form = SimpleAuthorForm()

>>> print form
<tr><th><label for="id_name">Name:</label></th><td><input id="id_name" type="text" name="name" maxlength="50" /></td></tr>
<tr><th><label for="id_last_name">Last name:</label></th><td><input id="id_last_name" type="text" name="last_name" maxlength="50" /></td></tr>
<tr><th><label for="id_birth_year">Birth year:</label></th><td><input type="text" name="birth_year" id="id_birth_year" /></td></tr>
<tr><th><label for="id_active">Active:</label></th><td><input type="checkbox" name="active" id="id_active" /></td></tr>

Then we can enable template-based output by setting `template_name`.

>>> form.template_name="forms/form.html"

>>> print form
<tr><th><label for="id_name" class="required">Name *:</label></th><td><input id="id_name" type="text" name="name" maxlength="50" /></td></tr>
<tr><th><label for="id_last_name" class="required">Last name *:</label></th><td><input id="id_last_name" type="text" name="last_name" maxlength="50" /></td></tr>
<tr><th><label for="id_birth_year" class="required">Birth year *:</label></th><td><input type="text" name="birth_year" id="id_birth_year" /></td></tr>
<tr><th><label for="id_active" class="required">Active *:</label></th><td><input type="checkbox" name="active" id="id_active" /></td></tr>

Or we can just directly create the form passing `template_name`.

>>> form = SimpleAuthorForm(template_name="forms/form.html")

>>> print form
<tr><th><label for="id_name" class="required">Name *:</label></th><td><input id="id_name" type="text" name="name" maxlength="50" /></td></tr>
<tr><th><label for="id_last_name" class="required">Last name *:</label></th><td><input id="id_last_name" type="text" name="last_name" maxlength="50" /></td></tr>
<tr><th><label for="id_birth_year" class="required">Birth year *:</label></th><td><input type="text" name="birth_year" id="id_birth_year" /></td></tr>
<tr><th><label for="id_active" class="required">Active *:</label></th><td><input type="checkbox" name="active" id="id_active" /></td></tr>

----

Let's excercise our extended ModelForm.

The bare bones, absolutely nothing custom, basic case.

>>> class BookForm(extended.ModelFormStdWidgets):
...     class Meta:
...         model = Book

>>> BookForm.base_fields.keys()
['title', 'isbn', 'author', 'active']

Let's instantiate the form and see which fields come from the form instance,
and in which order.

>>> form = BookForm()

>>> form.fields.keys()
['title', 'isbn', 'author', 'active']

Now let's try again, but specifying an ordering:

>>> form = BookForm(fieldorder=['active', 'title', 'author', 'isbn'])

>>> form.fields.keys()
['active', 'title', 'author', 'isbn']

>>> print form
<tr><th><label for="id_active">Active:</label></th><td><input checked="checked" type="checkbox" name="active" id="id_active" /></td></tr>
<tr><th><label for="id_title">Title:</label></th><td><input id="id_title" type="text" name="title" maxlength="200" /></td></tr>
<tr><th><label for="id_author">Author:</label></th><td><select name="author" id="id_author">
<option value="" selected="selected">---------</option>
<option value="1">Pablo Neruda</option>
<option value="2">William Shakespeare</option>
</select></td></tr>
<tr><th><label for="id_isbn">Isbn:</label></th><td><input id="id_isbn" type="text" name="isbn" maxlength="32" /></td></tr>

Then we can enable template-based output by setting `template_name`.

>>> form.template_name="forms/form.html"

>>> print form
<tr><th><label for="id_active">Active:</label></th><td><input checked="checked" type="checkbox" name="active" id="id_active" /></td></tr>
<tr><th><label for="id_title" class="required">Title *:</label></th><td><input id="id_title" type="text" name="title" maxlength="200" /></td></tr>
<tr><th><label for="id_author" class="required">Author *:</label></th><td><select name="author" id="id_author"><option value="" selected="selected">---------</option><option value="1">Pablo Neruda</option><option value="2">William Shakespeare</option></select></td></tr>
<tr><th><label for="id_isbn">Isbn:</label></th><td><input id="id_isbn" type="text" name="isbn" maxlength="32" /></td></tr>

Or we can just directly create the form passing `template_name`.

>>> form = BookForm(fieldorder=['active', 'title', 'author', 'isbn'], template_name="forms/form.html")

>>> print form
<tr><th><label for="id_active">Active:</label></th><td><input checked="checked" type="checkbox" name="active" id="id_active" /></td></tr>
<tr><th><label for="id_title" class="required">Title *:</label></th><td><input id="id_title" type="text" name="title" maxlength="200" /></td></tr>
<tr><th><label for="id_author" class="required">Author *:</label></th><td><select name="author" id="id_author"><option value="" selected="selected">---------</option><option value="1">Pablo Neruda</option><option value="2">William Shakespeare</option></select></td></tr>
<tr><th><label for="id_isbn">Isbn:</label></th><td><input id="id_isbn" type="text" name="isbn" maxlength="32" /></td></tr>

----

Ok, let's see how it gets with ForeignKey extended widget:

>>> class BookForm(extended.ModelForm):
...     class Meta:
...         model = Book
>>> form = BookForm(instance = book)
>>> print form
<tr><th><label for="id_title">Title:</label></th><td><input id="id_title" type="text" name="title" value="A Midsummer Night&#39;s Dream" maxlength="200" /></td></tr>
<tr><th><label for="id_isbn">Isbn:</label></th><td><input id="id_isbn" type="text" name="isbn" value="ABCD12" maxlength="32" /></td></tr>
<tr><th><label for="id_author">Author:</label></th><td><span class="nobreak"><select name="author" id="id_author">
<option value="">---------</option>
<option value="1">Pablo Neruda</option>
<option value="2" selected="selected">William Shakespeare</option>
</select>
<span class="related-buttons">
  <a href="/authors/" class="related-lookup" id="lookup_id_author" onclick="return showRelatedLookupPopup(this);">
    <img src="/media/img/admin/icon_searchbox.png" width="12" height="10" style="cursor: pointer;" alt="Select related item" title="Select related item" />
  </a>
  <a href="/authors/2/edit" class="related-edit" id="edit_id_author" onclick="return showRelatedEditPopup(this);">
    <img src="/media/img/admin/icon_changelink.gif" width="10" height="10" style="cursor: pointer;" alt="Edit related item" title="Edit related item" />
  </a>
  <a href="/authors/new/" class="related-add" id="add_id_author" onclick="return showRelatedAddPopup(this);">
    <img src="/media/img/admin/icon_addlink.gif" width="10" height="10" style="cursor: pointer;" alt="Add new related item" title="Add new related item" />
  </a>
</span></span></td></tr>
<tr><th><label for="id_active">Active:</label></th><td><input checked="checked" type="checkbox" name="active" id="id_active" /></td></tr>

----

Let's try widgets

>>> from softwarefabrica.django.forms.widgets import *

>>> dtw = DateTimeWidget()

>>> print dtw.render('birth_date', '25/11/2008 15:05')
<span class="nobreak">
  <span class="date">
    <input type="text" name="birth_date" value="25/11/2008 15:05" id="birth_date_id" />&nbsp;
    <img src="/static/images/icon_calendar.gif" alt="calendar" id="birth_date_id_btn" style="cursor: pointer;" title="Select date and time" />
    <script type="text/javascript">
    Calendar.setup({
        inputField     :    "birth_date_id",
        ifFormat       :    "%d/%m/%Y %H:%M",
        button         :    "birth_date_id_btn",
        singleClick    :    true,
        showsTime      :    true
    });
    </script>
  </span>
</span>

>>> dw = DateWidget()

>>> print dw.render('start_date', '20/11/2008')
<span class="nobreak">
  <span class="date">
    <input type="text" name="start_date" value="20/11/2008" id="start_date_id" />&nbsp;
    <img src="/static/images/icon_calendar.gif" alt="calendar" id="start_date_id_btn" style="cursor: pointer;" title="Select date" />
    <script type="text/javascript">
    Calendar.setup({
        inputField     :    "start_date_id",
        ifFormat       :    "%d/%m/%Y",
        button         :    "start_date_id_btn",
        singleClick    :    true,
        showsTime      :    false
    });
    </script>
  </span>
</span>

>>> riw = RelatedItemWidget()
>>> riw.model = Author

>>> print riw.render('author', neruda.id)
<span class="nobreak"><span class="related-buttons"><input type="text" name="author_textrepr" value="Pablo Neruda" id="id_author_textrepr" /><input type="hidden" name="author" value="1" id="author_id" /></span>&nbsp;
<a href="/authors/" class="related-lookup" id="lookup_id_author_id" onclick="return showRelatedLookupPopup(this);"><img src="/static/images/blue_view.gif" id="author_id_btn" style="cursor: pointer;" alt="Select related item" title="Select related item" /></a>
<a href="/authors/new/" class="related-add" id="add_id_author_id" onclick="return showRelatedAddPopup(this);"><img src="/static/images/12-em-plus.png" id="author_id_btn" style="cursor: pointer;" alt="Add new related item" title="Add new related item" /></a></span>

>>> from softwarefabrica.django.forms.fields import *
>>> import datetime

>>> class BookRentForm(extended.ModelFormStdWidgets):
...     class Meta:
...         model = BookRent

>>> form = BookRentForm()

>>> print form
<tr><th><label for="id_book">Book:</label></th><td><select name="book" id="id_book">
<option value="" selected="selected">---------</option>
<option value="1">A Midsummer Night&#39;s Dream (William Shakespeare)</option>
</select></td></tr>
<tr><th><label for="id_when">When:</label></th><td><input type="text" name="when" id="id_when" /></td></tr>

>>> class BookRentForm(extended.ModelFormStdWidgets):
...     when = DateTimeField()
...
...     class Meta:
...         model = BookRent

>>> form = BookRentForm()

>>> print form
<tr><th><label for="id_book">Book:</label></th><td><select name="book" id="id_book">
<option value="" selected="selected">---------</option>
<option value="1">A Midsummer Night&#39;s Dream (William Shakespeare)</option>
</select></td></tr>
<tr><th><label for="id_when">When:</label></th><td><span class="nobreak">
  <span class="date">
    <input type="text" name="when" id="id_when" />&nbsp;
    <img src="/static/images/icon_calendar.gif" alt="calendar" id="id_when_btn" style="cursor: pointer;" title="Select date and time" />
    <script type="text/javascript">
    Calendar.setup({
        inputField     :    "id_when",
        ifFormat       :    "%d/%m/%Y %H:%M",
        button         :    "id_when_btn",
        singleClick    :    true,
        showsTime      :    true
    });
    </script>
  </span>
</span></td></tr>

>>> class BookRentForm(extended.ModelForm):
...     class Meta:
...         model = BookRent

>>> form = BookRentForm()

>>> print form
<tr><th><label for="id_book">Book:</label></th><td><select name="book" id="id_book">
<option value="" selected="selected">---------</option>
<option value="1">A Midsummer Night&#39;s Dream (William Shakespeare)</option>
</select></td></tr>
<tr><th><label for="id_when">When:</label></th><td><span class="nobreak">
  <span class="date">
    <input type="text" name="when" id="id_when" />&nbsp;
    <img src="/static/images/icon_calendar.gif" alt="calendar" id="id_when_btn" style="cursor: pointer;" title="Select date and time" />
    <script type="text/javascript">
    Calendar.setup({
        inputField     :    "id_when",
        ifFormat       :    "%d/%m/%Y %H:%M",
        button         :    "id_when_btn",
        singleClick    :    true,
        showsTime      :    true
    });
    </script>
  </span>
</span></td></tr>

We could also use our version of modelform_factory()

>>> formC = extended.modelform_factory(BookRent, form=extended.ModelFormStdWidgets)

>>> form = formC()

>>> print form
<tr><th><label for="id_book">Book:</label></th><td><select name="book" id="id_book">
<option value="" selected="selected">---------</option>
<option value="1">A Midsummer Night&#39;s Dream (William Shakespeare)</option>
</select></td></tr>
<tr><th><label for="id_when">When:</label></th><td><span class="nobreak">
  <span class="date">
    <input type="text" name="when" id="id_when" />&nbsp;
    <img src="/static/images/icon_calendar.gif" alt="calendar" id="id_when_btn" style="cursor: pointer;" title="Select date and time" />
    <script type="text/javascript">
    Calendar.setup({
        inputField     :    "id_when",
        ifFormat       :    "%d/%m/%Y %H:%M",
        button         :    "id_when_btn",
        singleClick    :    true,
        showsTime      :    true
    });
    </script>
  </span>
</span></td></tr>

If we need to personalize the widgets, we can do so by overriding the
formfield callback in our version of modelform_factory()

>>> formC = extended.modelform_factory(BookRent, form=extended.ModelForm, formfield_callback=lambda f, cb=extended.extended_formfield_cb: cb(f, old_datewidgets=True))

>>> form = formC()

>>> print form
<tr><th><label for="id_book">Book:</label></th><td><select name="book" id="id_book">
<option value="" selected="selected">---------</option>
<option value="1">A Midsummer Night&#39;s Dream (William Shakespeare)</option>
</select></td></tr>
<tr><th><label for="id_when">When:</label></th><td><input type="text" name="when" id="id_when" /></td></tr>

"""
