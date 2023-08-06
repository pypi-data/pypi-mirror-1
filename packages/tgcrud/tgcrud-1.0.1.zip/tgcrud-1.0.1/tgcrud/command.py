import pkg_resources
from turbogears.util import get_package_name, load_project_config
import optparse
from paste.script import create_distro
from turbogears.command.quickstart import TGTemplate
from turbogears import config

class CrudTemplate(TGTemplate):
    #egg_plugins = ["tgcrud"]
    #required_template = [""]
    _template_dir = pkg_resources.resource_filename(
                        "tgcrud.templates",
                        "crud")
    #use_cheetah = True
    summary = "tg crud base template"

class CrudSOTemplate(TGTemplate):
    required_template = ["tgcrudbase"]
    _template_dir = pkg_resources.resource_filename(
                        "tgcrud.templates",
                        "crudso")
    #use_cheetah = True
    summary = "tg crud sqlobject template"

class CrudSATemplate(TGTemplate):
    required_template = ["tgcrudbase"]
    _template_dir = pkg_resources.resource_filename(
                        "tgcrud.templates",
                        "crudsa")
    #use_cheetah = True
    summary = "tg crud sqlalchemy template"

class CrudCommand:
    """
    Generate admin interface from template

    $ tg-admin crud [model class name] [package name]
    """

    desc = "Create management interface"
    need_project = True

    modelname = None
    modelpackage = None
    templates = "tgcrudso tgcrudbase"
    sqlalchemy = False
    primary_id = 'id'
    # auto detect sqlalchemy and assign templates
    if get_package_name() is not None:
        load_project_config()
    db = config.get('sqlalchemy.dburi')
    #print 'SQLAlchemy db: '+str(db)
    if db:
        print "...detected"
        sqlalchemy = True
        templates = "tgcrudsa tgcrudbase"
    else:
        sqlalchemy = False
        templates = "tgcrudso tgcrudbase"
    
    package = get_package_name()
    name = package

    def __init__(self,*args, **kwargs):
        parser = optparse.OptionParser(
                    usage="%prog crud [model name] [modelpackage name]")
        parser.add_option("-m", "--model",
            help="class name in the model",
            dest="modelname")
        parser.add_option("-p", "--package",
            help="package name for the code",
            dest="modelpackage")
        parser.add_option("--dry-run",
            help="dry run (don't actually do anything)",
            action="store_true", dest="dry_run")
        parser.add_option("-t", "--templates",
            help="user specific templates",
            dest="templates", default = self.templates)
        parser.add_option("-s", "--sqlalchemy",
            help="use SQLAlchemy instead of SQLObject",
            action="store_true", dest="sqlalchemy", default = self.sqlalchemy)
        parser.add_option("-i", "--id",
            help="model primary key",
            dest="primary_id", default = self.primary_id)
        (options, args) = parser.parse_args()
        self.__dict__.update(options.__dict__)
        if args:
            self.modelname = args[0]
            try:
                self.modelpackage = args[1]
                print args[1]
            except:
                self.modelpackage = None

    def run(self):
        "Generate the template"
        while not self.modelname:
            print "Note: Make sure you have created your models first"
            self.modelname = raw_input("Enter the model name: ")
        while not self.modelpackage:
            modelpackage = self.modelname.capitalize()
            self.modelpackage = raw_input("Enter the package name [%s]: "
                                    % modelpackage)
            if not self.modelpackage:
                self.modelpackage = modelpackage

        #check for lib name conflict
        import imp
        try:
            if imp.find_module(self.modelpackage):
                print "the package name %s is already in use"%self.modelpackage
                return
        except ImportError, e:
            print e
        
        # manually setup orm options
        if self.sqlalchemy:
            self.templates = "tgcrudsa tgcrudbase"
        else:
            self.templates = "tgcrudso tgcrudbase"
            
        #TODO: handle directory conflict
        command = create_distro.CreateDistroCommand("create")
        cmd_args = []
        for template in self.templates.split(" "):
            cmd_args.append("--template=%s" % template)
        cmd_args.append(self.name)
        cmd_args.append("modelname=%s" %self.modelname)
        cmd_args.append("modelpackage=%s" % self.modelpackage)
        cmd_args.append("package=%s" % self.package)
        cmd_args.append("sqlalchemy=%s" % self.sqlalchemy)
        cmd_args.append("id=%s" % self.primary_id)
        if self.dry_run:
            cmd_args.append("--simulate")
            cmd_args.append("-q")

        try:
            command.run(cmd_args)
        except:
            #hide the wrong location of paste egg-txt
            pass

