from setuptools import setup, find_packages
setup(
    name = "django-flashcookie",
    version = "0.1.5",
    packages = find_packages(),
    author = "Anderson",
    author_email = "self.anderson@gmail.com",
    description = "This django application provides rails-like flash messages to Django framework.",
    long_description = """
Example:
----------

**views.py**
::

    def some_action(request):
        ...
        request.flash['error'] = "You can't post comments in this section"
        return HttpReponseRedirect("/")


**base.html**
::

    {% if flash %}
        {% for message in flash.error %}
            {{ message }}
        {% endfor %}
    {% endif %}
                              

Download:
----------
    hg clone http://bitbucket.org/offline/django-flashcookie/

    """,
    license = "BSD",
    keywords = "django",
    url = "http://bitbucket.org/offline/django-flashcookie/wiki/Home",
)

