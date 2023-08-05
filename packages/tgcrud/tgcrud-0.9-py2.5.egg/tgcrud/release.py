# Release information about tgcrud


version = "0.9"

description = "Genrate CRUD interface in TurboGears"
long_description = """
tgcrud is a 'no magic' crud (create, read, update, delete) 
interface generator, 
and the generated codes are fully customizable.
tgcrud heavily use form widgets and show you many 
TG 1.0 features in it's controllers/templates.

If you are a TG beginer, tgcrud could generate a admin skeleton based on your model. 

If you are an experienced TG developer, you could get it in minutes
since it just done the basic procedure that every time you write a
management interface of your model.

Install
----------

The 'tgcrud' command extension is available in Python CheeseShop and TurboGears svn. 

You can use setuptools to install tgcrud with following command::

::

    $ easy_install tgcrud

or download the source code and install tgcrud manually.

Usage
----------
1. Define your model in model.py

2. After you've defined your model,
   you could use "tg-admin crud" command to generate the crud pack.
   The syntax is::

       $ tg-admin crud [model class name] [package name]

   e.x if the model name is BookMark,
   the package name is BookMarkController, the command is::

       $ tg-admin crud BookMark BookMarkController

   Then the 'admin' package is generated.
   You just need take several minutes to customize the formfield to
   have a proper crud interface.

3. Import the package to your controllers.py with a line:

   from BookMarkController import BookMarkController

   and add a branch on your Root()::

       foo = BookMarkController()

4. Customize the form filed in admin/controllers.py

5. Open the http://localhost:8080/foo to use the customizable interface.

Please refer to http://docs.turbogears.org/1.0/CRUDTemplate for detail"""
author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2007"

# if it's open source, you might want to specify these
url = "docs.turbogears.org"
download_url = "http://www.python.org/pypi/tgcrud/"
license = "MIT"
