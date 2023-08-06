.. contents::

===========
Search Form
===========

Search Form is a Django application that lets you create very fancy search
forms in your project. Some of its main features are:

  * Easy to use: add, edit and remove search terms with very few clicks and
    keystrokes
  * Easy to integrate: just subclass Search Form and add your search terms
  * Easy to customize: you can change the default search terms, or change
    their layouts with custom templates or maybe change the style using CSS
  * Accesible: it works with no javascript degrading gracefully to a nighties
    version

Search Form is distributed under the terms of the `GNU Lesser General Public
License <http://www.gnu.org/licenses/lgpl.html>`_.

Documentation
=============

Installation
------------

Search Form depends on jQuery 1.2.X so you need to download it and put
in your media directory. After that you can install search form. Just type::

  easy_install searchform

and Easy Install will go to the Cheeseshop and grab the last searchform for
you. It will also install it for you in your site-packages directory at no
extra cost :-)

Tutorial
--------

Using search form is quite simple. Just follow these simple steps:

  #. Add 'searchform' to your INSTALLED_APPS tuple in your settings.py. This
     is neccesary so Django can find the default searchform templates.
  #. Add the following url to your urls.py before your regular media url::

      (r'^media/searchform/', include('searchform.urls'))

Now, suppose you have this simple model in your application::

  class Animal(models.Model):
      name = models.CharField(max_length=100)
      weight = models.CharField(max_length=100)
      max_speed = models.IntegerField()

And you want to make a search form that lets your users find animals in your
wild database::

  from django.utils.datastructures import SortedDict

  from searchform.forms import SearchForm
  from searchform.terms import TextSearchTerm

  class AnimalSearchForm(SearchForm):
      fields = SortedDict((
          ('name': TextSearchForm('The name', 'Name', 'which name')),
          ('weight': TextSearchForm('The weight', 'Weight', 'which weight')),
          ('max_speed': TextSearchForm('The max speed', 'Speed', 
                                       'which max speed')),
          ))

Believe it or not that's all the python code you need to write to set up your
search form. Now it's time to use it in your views::

  def advanced_search(request):
      form = AnimalSearchForm('Find animals!', None)
      return render_to_response('your_template.html', {'form': form})


Finally let's see how your template looks like::

  {% extends "base.html" %}

  {% block extrahead %}
    <script type="text/javascript" src="{{ MEDIA_URL }}js/jquery-1.2.6.js"></script>
    {{ form.render_media|safe }}
  {% endblock %}

  {% block content %}
  <div id="search_form">

    <form action="{% url yourapp.views.search_results %}" method="get">
      {{ form }}
    </form>

  </div>
  {% endblock %}

Two things worth noting here:

  * You need to include jQuery **before** the media of the form
  * The search form must have the id 'search_form'


TODO: explain how to customize the templates and how to write custom search
terms. Explain what the QueryStringManager is

Development
===========

You can get the last bleeding edge version of searchform by doing a checkout
of its subversion repository::

  svn co https//svnpub.yaco.es/djangoapps/searchform/trunk searchform

Bug reports, patches and suggestions are more than welcome. Just put them
in our Trac system::

  https://tracpub.yaco.es/djangoapps/SearchForm

