# Release information about tgcrud


version = "1.0.2"

description = "Genrate CRUD interface in TurboGears"
long_description = """
tgcrud is an  TurboGears command extension,
which could generate a sqlobject/sqlalchemy backend 
editor/crud (create, read, update, delete) interface based 
on your Model with kid template. 
It could be plugged into any projects even if you don't use kid template.

The generated codes are fully customizable.
tgcrud heavily use form widgets and show you many
TG 1.0 features in it's controllers/templates.

Please refer to http://docs.turbogears.org/1.0/CRUDTemplate for detail

The command follow the TurboGears quickstart template style,  you could easily add
identity, form validation, paginate in your crud interface. 

If you are a TG beginer, tgcrud help you create a general
admin skeleton based on your model.

If you are an experienced TG developer, you could get it in minutes
since it just done the basic procedure that every time you write a
management interface of your model.

Features
----------------------

Fully customizable admin interface (the create, read, update, delete functions) with easy to extend(form validation, identity, paginate) templates.

No Magic

    * The generated codes are normal TG source.
    * No extra magic encapsulation. No need to rewrite the interface when you need extra flexibility (not the same as Rails'scaffold)
    * Separate Form definition from Model (not the same as  Django admin)
    * Use standard TurboGears syntax and code organization.
    * It's a good crud implementation reference by TG.

TurboGears

    * Bundles a TurboGears "tg-admin crud" command.
    * Support SQLObject and SQLAlchemy models
    * tgcrud kid interface works for you no matter whatever template engine you currently choose for your project.
    * You could customize the model relationship by widgets(document shows how to customize 1-to-1, 1-to-many, many-to-many relationship with widgets. Or you could do it in your way)
    * Takes advantage of TurboGears form widgets and validation. you'd hardly need to modify the HTML.

    
Install
----------

The 'tgcrud' command extension is available in Python CheeseShop and
TurboGears svn.

You can use setuptools to install tgcrud with following command::

    $ easy_install tgcrud

or download the source code and install tgcrud manually.

Screencast
--------------

Yes, there's a 'Make a Book Site with TurboGears' screencast with tgcrud.

If you are an experienced TG developer, you could skip to the third.

If you are new to TG, you may want to watch all of them to get familiar with TurboGears.

	- Quickstart TurboGears project, 6.5MB
	
	  http://files.turbogears.org/video/openbook1.swf
	
	- Design model with toolbox utilities, 7.7MB
	
	  http://files.turbogears.org/video/openbook2.swf
	
	- tgcrud, the TG's scaffold, 5.2 MB
	
	  http://files.turbogears.org/video/openbook3.swf

With tgcrud you could easily generate a Rails scaffold
style CRUD interface. The difference is all code in tgcrud is
implicit, which leads to more easy customization.

Usage
----------

	1. Define your model in model.py
	
	2. Once you've defined your model,
	   you could use "tg-admin crud" command to generate the crud pack.
	   The syntax is::
	
	       $ tg-admin crud [model class name] [package name]
	
	   e.x if the model name is BookMark,
	   and the package name we want is BookMarkController, the command is::
	
	       $ tg-admin crud BookMark BookMarkController
	
	   Then the 'admin' package is generated.
              
	   You just need take several minutes to customize the formfield to
	   have a proper crud interface.
	
	   ..note:: you could estimate the result by passing "--dry-run" to the command, such as::
	
	           $ tg-admin crud BookMark BookMarkController --dry-run
	
	       With this argument the command will not effect your physical directories. 
	
	
	3. Import the package to your controllers.py with a line:
	
	   from BookMarkController import BookMarkController
	
	   and add a branch on your Root()::
	
	       foo = BookMarkController()
	
	4. Customize the form filed in admin/controllers.py
	
	5. Open the http://localhost:8080/foo to use the customizable interface.

Please check http://docs.turbogears.org/1.0/CRUDTemplate for detail instructions.

ChangeLog
-------------------------

1.0.2
    * Expand compatibility to all TurboGears 1 version

1.0.1
    * Minor template updates

1.0
    * Fully SQLAlchemy support with
        * SQLObject/SQLAlchemy auto detection 
        * Able to specify the primary id
    * Minor template updates

"""

author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2007, 2008"

# if it's open source, you might want to specify these
url = "http://docs.turbogears.org/1.0/CRUDTemplate"
download_url = "http://www.python.org/pypi/tgcrud/"
license = "MIT"
