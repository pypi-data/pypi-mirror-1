django-clippy - Writing to the Clipboard from within Webpages
=============================================================

django-clippy provides a template tag for the [Django Web Framework][1] 
to allow copying the Clipboard.

    {% load clippy %}
    <p><input id="clipfield" value="Data in Field"> {% clippy "clipfield" %}

Here is what Clippy looks like on GitHub:

![Clippy in action](http://img.skitch.com/20090213-cjiawnwig8udf5a6qf1c45cne8.png)

To install copy [`clippy/static/clippy.swf`][2] into your MEDIA_ROOT and put the
`clippy` directory somewhere into your Python path. If you have [pip][3]
installed `pip install django-clippy` should do the job. Or get it at 
[http://github.com/mdornseif/django-clippy](http://github.com/mdornseif/django-clippy)
or at [the Python Package Index][4].

Add `"clippy"` to your
`INSTALLED_APPS` in your `settings.py`. This should be enough to use the
{% clippy "id" %} template tag in your templates.

The template tag needs the id of the field you want to copy to the clipboard
as a parameter. You can give it an additional parameter describing the
background color to use for the widget.

    {% clippy "someid" "#FF0000" %}

If you don't give a color, the color given in `settings.CLIPPY_BGCOLOR` is
used. It `CLIPPY_BGCOLOR` is not set, `#ffffff` is used as a fall back.

The code comes with a demo application. If you have [pip][3] and
[virtualenv][5] installed, just type `make dependencies runserver`
and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to play with it.

If you see errors like `ImportError: No module named django-clippy-1.0`
ensure that your durrend directory name has no dots and spaces in it.
E.g. `cd ..; mv django-clippy-1.0 django-clippy-10; cd django-clippy-10`.


[1]: http://www.djangoproject.com/
[2]: http://github.com/mdornseif/django-clippy/raw/master/clippy/static/clippy.swf
[3]: http://pypi.python.org/pypi/pip
[4]: http://pypi.python.org/pypi/django-clippy/
[5]: http://pypi.python.org/pypi/virtualenv


Using the Flash Widget without Django
-------------------------------------

The "copy to clipboard" functionality is not reliably available in Javascript
therefore it is implemented in Flash. If you don't use Django, you obviously
can use the Flash widged directly in your HTML code. It can be called like
this:

    <span id="someid">Somevalue</span>
    <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
            width="110" height="14" id="clippy_someid">
        <param name="movie" value="/mymedia/clippy.swf"/>
        <param name="allowScriptAccess" value="always" />
        <param name="quality" value="high" />
        <param name="scale" value="noscale" />
        <param NAME="FlashVars" value="id=someid">
        <param name="bgcolor" value="#ffffff">
        <embed src="/mymedia/clippy.swf?x=23"
            width="110" height="14" name="clippy" quality="high"
            allowScriptAccess="always"
            type="application/x-shockwave-flash"
            pluginspage="http://www.macromedia.com/go/getflashplayer"
            FlashVars="id=someid" bgcolor="#ffffff" /></object>

The widget understands the following parameters:

* `id` - mandantory. Id from which the 
* `copied` - text to display after copying. Default is "copied!"
* `copyto` - text to display before copying. Default is "copy to clipboard"
* `callBack` - Javascript function to be called after copying



Compiling the Flash Widget
--------------------------

In order to compile Clippy from source, you need to install the following:

* [haXe](http://haxe.org/)
* [swfmill](http://swfmill.org/)

The haXe code is in `Clippy.hx`, the button images are in `assets`, and the
compiler config is in `compile.hxml`. Make sure you look at all of these to
see where and what you'll need to modify. To compile everything into a final
SWF, type `make flash`.

If that is successful `clippy/static//clippy.swf` should be the new flash
widged which you need to copy to your `MEDIA_PATH`.



History
-------

The original clippy code is by Tom Preston-Werner. This version contains
Fixes by Zhang Jinzhu and Kyle Neath. Maximillian Dornseif integrated various
patches and created the Django template Tag. Check the
[GitHub Fork Network][4] to better understand the project history.

[4]: http://github.com/mojombo/clippy/network



License
-------

MIT License (see LICENSE file)
