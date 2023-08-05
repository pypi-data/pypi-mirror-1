# Release information about tgcrud

version = "0.8"

description = "Genrate CRUD interface"
long_description = """
1. Define your model in model.py
2. After you've defined your model, you could use "tg-admin crud" command (Note 1) to generate the crud pack. The syntax is:

   $ tg-admin crud [model class name] [package name]

 e.x if the model name is BookMark, the package name is BookMarkController, the command is:

 $ tg-admin crud BookMark BookMarkController

 Then then the 'admin' package is generated(Note 2). You just need take several minutes to customize the formfield to have a proper crud interface.

3. Import the package to your controllers.py with a line:

   from admin import admin

 and add a branch on your Root():

 foo = admin()

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
