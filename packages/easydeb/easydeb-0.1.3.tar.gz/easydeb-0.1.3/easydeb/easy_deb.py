#!python
import sys, os, glob, shutil, distutils.core, fileinput, tempfile 
import re, tarfile, datetime, commands, pickle, pkg_resources
import pwd, getpass, socket, ConfigParser
from optparse import OptionParser
req = "setuptools>="+"0.6a0"
pkg_resources.require(req)

import easy_install
from setuptools import package_index 
from setuptools.command.easy_install import main
from setuptools.archive_util import unpack_archive
from setuptools.package_index import URL_SCHEME


def sed( filename, find, replace, dest=1, tostring=0):
    """This function does text substitutions like sed does"""
    if isinstance (dest,int):
        inplace=dest
        for l in fileinput.input(filename,inplace):
            print re.sub(find, replace,l),
    else:
        inplace=0
        f_dest=file(dest,"a+")
        f_input=file(filename,"r+")
        for l in f_input:
            f_dest.write(re.sub(find, replace,l))
        
def extensions( filename ):
    """This function searches for extensions in setup.py"""
    f_input=file(filename,"r")
    for l in f_input:
        if re.search('Extension',l):
            if not re.search('#.*Extension',l):
                return True
    return False
        
class Easy_deb:
    def __init__(self,req_string=None, pyvers=["2.3","2.4"], deps=None,
            bdeps=None, find_links=[], dest_base_dir=".", arch_dep=False ):
        self.requirement        = req_string
        self.index              = package_index.PackageIndex()
        self.found              = None
        self.dest               = None
        self.filename           = None
        self.source_dir         = None
        self.project_fullname   = None
        self.deps_database      = None
        self.metadata           = {} 
        self.pyvers             = pyvers
        self.deps               = deps
        self.bdeps              = bdeps
        self.find_links         = find_links
        self.dest_base_dir      = os.path.abspath(dest_base_dir)
        self.template_dir       = pkg_resources.resource_filename(__name__, 'template')
        self.arch_dep           = arch_dep
        self.options_store_dir  = os.path.join('/','usr','share','pypi','options')
        self.config_file        = os.path.join('/','etc','easydeb','config.cfg')
        self.mapping_dbs         = [os.path.join('/','etc','easydeb','common','mapping.db')]
        self.debian_release     = "-1"
        u=pwd.getpwnam(getpass.getuser())
        self.maintainer         = "%s <%s@%s>" %(u[4].split(",")[0], u[0], socket.getfqdn())
        self.parse_config()
   
    def parse_options(self,options):
        try:
            self.requirement        = options.spec
            self.deps               = options.deps
            self.bdeps              = options.bdeps
            self.find_links         = options.find_links.split(',')
            self.arch_dep           = options.arch_dep
            if options.versions:
                self.pyvers         = options.versions.split(",")
            if options.dest_dir: 
                self.dest_base_dir  = os.path.abspath(options.dest_dir)
            if options.options_store_dir:
                self.options_store_dir   = os.path.abspath(options.options_store_dir)
            if options.config_file:
                self.config_file    = os.path.abspath(options.config_file)
            if options.debian_release:
                self.debian_release    = options.debian_release
        except AttributeError:
            pass

    def parse_config(self):
        if not  os.path.exists(self.config_file):
            raise IOError, "Config file %s not found." % self.config_file
        config_f= open(self.config_file)
        config = ConfigParser.ConfigParser()
        config.readfp(config_f)
        
        if config.has_option( "easydeb", "options-dir" ):
            self.options_store_dir   = config.get(  "easydeb", "options-dir" ) 
        if config.has_option( "easydeb", "pyvers" ): 
            self.pyvers         = config.get(  "easydeb", "pyvers").split(",") 
        if config.has_option( "easydeb", "dest-dir" ):
            self.dest_base_dir  = config.get(  "easydeb", "dest-dir" )
        if config.has_option( "easydeb", "maintainer" ):
            self.maintainer     = config.get(  "easydeb", "maintainer" )
        if config.has_option( "easydeb", "mapping-dbs"):
            self.mapping_dbs = [ os.path.expanduser(d.strip()) for d in config.get( "easydeb", "mapping-dbs").split(',') ]
            
        config_f.close()
        
    def require(self, dep, version=""):
        ret=""
        if dep=="setuptools":
            return ret
        if not self.deps_database:
            database=self.mapping_dbs[0]
            if not  os.path.exists(database):
                raise IOError, "Database file %s not found." % database
            deps_f= open(database)
            self.deps_database = ConfigParser.ConfigParser()
            self.deps_database.readfp(deps_f)
            deps_f.close()
            if self.mapping_dbs[1:]:
                self.deps_database.read(self.mapping_dbs[1:])
            
        if self.deps_database.has_option( "easydeb", dep ):
            dep_line=self.deps_database.get( "easydeb",dep)
            num_deps=len(dep_line.split(','))
            if version and num_deps==1:
                self.bdeps+=", %s %s" % (dep_line, version)
                ret=(dep_line, version).__str__()
            else:
                self.bdeps+=", %s" % dep_line
                ret=dep_line
        elif not self.deps_database.has_section("easydeb"):
            raise IOError, "[easydeb] section missin in "+ database
        ret+= '\n'
        return ret
        

    def load_deps(self, pkg_info):
        
        
        f_input=file(pkg_info,"r+")
        req_re=re.compile("^Requires:")
       
        deps=""
        for l in f_input:
            if req_re.search(l):
                deps += l[10:].split().__str__()
                deps += self.require( * (l[10:].split()) )
        if deps:
            print "###### Found Dependencies ######"
            print deps,"\n################################"

        
    def download_source(self):
        """Download source modules"""
        must_download=True
        if os.path.exists(self.requirement):
            must_download=False
            self.filename=self.requirement
            self.found=package_index.distros_for_filename(self.filename).next()
            print "Using file", self.filename
        elif URL_SCHEME(self.requirement):
            self.found=package_index.distros_for_url(self.requirement).next()
        else:    
            self.requirement=pkg_resources.Requirement.parse(self.requirement)
            for link in [l.strip() for l in self.find_links if l]:
                self.index.scan_url(link)
            self.index.find_packages(self.requirement)
            for dist in self.index[self.requirement.key]:
                if dist.precedence == package_index.SOURCE_DIST:
                    self.found=dist
        if self.found:
            self.dest=os.path.join(self.dest_base_dir,'deb-pkg-'+pkg_resources.safe_name(self.found.project_name).lower()+'-'+self.found.version)
        else:
            print "Distribution not found"
            raise pkg_resources.DistributionNotFound
        if os.path.isdir(self.dest):
            shutil.rmtree(self.dest)
        os.makedirs(self.dest)
       
        if must_download:
            print "\nDownloading ", self.found.location, '.\n'
            self.filename=self.index.download(self.found.location, self.dest)

    def unpack(self):
        """Unpack found archive"""
        if not os.path.exists(self.filename):
            raise IOError, "file ("+self.filename+") not found"
        unpack_archive(self.filename, self.dest)
        setups = glob.glob(os.path.join(self.dest, '*', 'setup.py'))
        unpacked = os.path.abspath(os.path.dirname(setups[0]))
        self.project_fullname = "python-pypi-"+pkg_resources.safe_name(self.found.project_name).lower()+'-'+self.found.version 
        self.source_dir = os.path.join(self.dest,  self.project_fullname)
        if not (unpacked == self.source_dir):
            shutil.copytree(unpacked, self.source_dir)
            shutil.rmtree(unpacked)
        tar_file=os.path.join(self.dest, self.project_fullname+'.orig.tar.gz')
        tar = tarfile.open(tar_file, "w:gz")
        tar.add(self.source_dir)
        tar.close()

    def deb_src(self):
        """Create debain source package"""
        if not os.path.exists(self.source_dir):
            raise IOError, "source dir ("+self.source_dir+") not found"
        sys.path.append(self.source_dir)
        debian_dir=os.path.join(self.source_dir,'debian')
        if os.path.exists(debian_dir):
            shutil.rmtree(debian_dir)
        shutil.copytree(os.path.join(self.template_dir,'copy'),debian_dir)
       
        os.chdir(self.source_dir)
        
        self.metadata['name']=commands.getoutput("python setup.py --name |tail -1")
        self.metadata['version']=commands.getoutput("python setup.py --version |tail -1")
        self.metadata['author']=commands.getoutput("python setup.py --author |tail -1")
        self.metadata['author_email']=commands.getoutput("python setup.py --author-email |tail -1")
        self.metadata['location']=commands.getoutput("python setup.py --url |tail -1")        
        self.metadata['description']=commands.getoutput("python setup.py --description |tail -1")
        self.metadata['long_description']=commands.getoutput("python setup.py --long-description")        
        
        #Check for deps
        if os.path.exists(os.path.join(self.source_dir,"PKG-INFO")):
            self.load_deps(os.path.join(self.source_dir,"PKG-INFO"))
            
        pkg_name=re.sub("_", "-", pkg_resources.safe_name(self.metadata['name'])).lower()
       
        #Control file from templates
        if self.bdeps:
            self.bdeps="python%v, python%v-setuptools (>= 0.6a1-2), python%v-dev, " + self.bdeps
        else:
            self.bdeps="python%v, python%v-setuptools (>= 0.6a1-2), python%v-dev"
        
        if self.deps:
            self.deps="python%v-setuptools (>= 0.6a1-2), " + self.deps
        else:
            self.deps="python%v-setuptools (>= 0.6a1-2)"

        bdeps_v_l=[d.strip() for d in self.bdeps.split(',') if "%v" in d]
        
        bdeps_v=bdeps_v_l[0]
        for d in bdeps_v_l[1:]:
            bdeps_v+=', '+d
        extensions_present=self.arch_dep or extensions(os.path.join(self.source_dir,"setup.py"))
                
        if extensions_present:
             self.deps+=", ${shlibs:Depends}"
             
        deps=re.sub("%v", "", self.deps) 
        bdeps=re.sub("%v", "", self.bdeps)
        sed(os.path.join(debian_dir, "control"), "%%DEPS%%", deps)

        if self.pyvers != 'all':
            for version in self.pyvers:
                deps=re.sub("%v", version, self.deps)
                bdeps+=', '+re.sub("%v", version, bdeps_v)
                sed(os.path.join(self.template_dir, "control.template"), "%%PYVERS%%", version, dest=os.path.join(debian_dir, "control"))
                sed(os.path.join(debian_dir, "control"), "%%DEPS%%", deps)
            
        sed(os.path.join(debian_dir, "control"), "%%PKGNAME%%", pkg_name)
        sed(os.path.join(debian_dir, "control"), "%%DESCRIPTION%%", self.metadata['description'])
        sed(os.path.join(debian_dir, "control"), "%%BUILDDEPS%%", bdeps)
        sed(os.path.join(debian_dir, "control"), "%%MAINTAINER%%", self.maintainer)
    
        #Setup architecture
        if extensions_present:
             sed(os.path.join(debian_dir, "rules"), "%%BINARY_PLATFORM%%", "binary-arch") 
             sed(os.path.join(debian_dir, "control"), "%%ARCH%%", "any")
        else:        
             sed(os.path.join(debian_dir, "rules"), "%%BINARY_PLATFORM%%", "binary-indep") 
             sed(os.path.join(debian_dir, "control"), "%%ARCH%%", "all")              
        
        #Other files from templates
        sed(os.path.join(debian_dir, "rules"), "%%PKGNAME%%", 
                pkg_name)
        sed(os.path.join(debian_dir, "rules"), "%%MODULENAME%%",
                self.metadata['name'])
        
        if  self.pyvers != 'all':
            sed(os.path.join(debian_dir, "rules"), "%%INSTALL_VERSIONS_TARGET%%", "install")
            sed(os.path.join(debian_dir, "rules"), "%%INSTALL_CD_TARGET%%", "fake-install")
        else:
            sed(os.path.join(debian_dir, "rules"), "%%INSTALL_VERSIONS_TARGET%%", "fake-install")
            sed(os.path.join(debian_dir, "rules"), "%%INSTALL_CD_TARGET%%", "install")
            
        os.chmod(os.path.join(debian_dir, "rules"), 0777)
        
        sed(os.path.join(debian_dir, "changelog"), "%%PKGNAME%%", pkg_name)
        sed(os.path.join(debian_dir, "changelog"), "%%DIST%%", "hoary")
        sed(os.path.join(debian_dir, "changelog"), "%%VERSION%%", self.metadata['version']+'-'+self.debian_release)
        sed(os.path.join(debian_dir, "changelog"), "%%DESCRIPTION%%", "Generated using easy_deb for " + "Ubuntu")
        email=self.metadata['author_email'].split(" ")[0]
        sed(os.path.join(debian_dir, "changelog"), "%%AUTHOR%%", self.metadata['author'] + ' <' + email + '>')

        #README.Debian from templates
        sed(os.path.join(debian_dir, "README.Debian"), "%%DESCRIPTION%%", self.metadata['description'])
        sed(os.path.join(debian_dir, "README.Debian"), "%%LONGDESCRIPTION%%", self.metadata['long_description'])
        sed(os.path.join(debian_dir, "README.Debian"), "%%DATE%%", datetime.datetime.now().__str__())
        sed(os.path.join(debian_dir, "README.Debian"), "%%LOCATION%%", self.found.location)
        
    def create(self):
        self.download_source()
        self.unpack()
        self.deb_src()
        print "\nPackage '%s' created in '%s'.\nSources in '%s'.\n" % (self.project_fullname, self.dest, self.source_dir)

def main(sysargs):
    parser = OptionParser("usage: %prog [options] (pypi-modulename | archive-file-name| url)")
    
    parser.add_option("-v", "--python-versions", type="string", dest="versions", 
            help="Coma separated list of python versions to package for. E.g.: -v 2.3,2.4 ",
            default="")
    
    parser.add_option("-d", "--debian-deps", type="string", dest="deps", 
            help="Standard debian dependency string. %v is replaced with python version",
            default="")
    
    parser.add_option("-b", "--debian-build-deps", type="string", dest="bdeps", 
            help="Standard debian dependency string. %v is replaced with python version",
            default="")
    
    parser.add_option("-f", "--find-links", type="string", dest="find_links", 
            help="Additionnal links to scan. Comma separated",
            default="")
    
    parser.add_option("-D", "--dest-dir", type="string", dest="dest_dir", 
            help="Distribution downloaded into file",
            default="")
    
    parser.add_option("-r", "--debian-release", type="string", dest="debian_release", 
            help="Debian release number",
            default="")
    
    parser.add_option("-m", "--mapping-dbs", type="string", dest="mapping_dbs", 
            help="Comma separated list of mapping file locations",
            default="")
    
    parser.add_option("--options-dir", type="string", dest="options_store_dir", 
            help="Directory where options defaults per module are stored",
            default="")
    
    parser.add_option("--config-file", type="string", dest="config_file", 
            help="Config file location",
            default="")
    
    parser.add_option("-c", "--common-dir",
            action="store_true", dest="common_dir", default=False,
            help="Install to commond dir from where tree linking is done")
    
    parser.add_option("-a", "--arch-dep",
            action="store_true", dest="arch_dep", default=False,
            help="Build arch dep packages")
   
    parser.add_option("-u", "--update-default-options", action="store_true",
            dest="update_default_options", default=False,
            help="Update the default options for this python module")
    
   
    (options, args) = parser.parse_args(sysargs[1:])
  

    if len(args) == 1 :
        spec=args[0]
        options._update_loose({'spec':spec})
    
        if options.common_dir:
            options.versions='all'
        
        ed = Easy_deb()
        ed.parse_config()
        ed.parse_options(options)
        
        try:
            if os.path.exists(spec):
                prj_name=package_index.distros_for_filename(spec).next().project_name
            elif URL_SCHEME(spec):
                prj_name=package_index.distros_for_url(spec).next().project_name
            else:    
                prj_name=""
        except:
           print "Error processing parameter '%s'. Not Found." % spec
           
        if prj_name and os.path.exists(os.path.join(ed.options_store_dir,prj_name)):
            pickle_file=open(os.path.join(ed.options_store_dir,prj_name))
            options_loaded=pickle.load(pickle_file)
            pickle_file.close()
            (options,arg)=parser.parse_args(sysargs[1:],options_loaded)
            ed.parse_options(options)
            print "Using stored options \n %s \n" % options
 
        
        ed.create()
        
        if options.update_default_options:
            options.update_default_options=False
            options.dest=""
            options.options_store_dir=""
            if not os.path.exists(ed.options_store_dir):
                try:
                    os.mkdir( ed.options_store_dir )
                except IOError:
                    os.system("sudo python -c"+
                        "'import os"+
                        "os.mkdir(%s)'"% ed.options_store_dir)
            
            must_copy=False
            try:
                pickle_file=open(os.path.join(ed.options_store_dir,ed.metadata['name']),'w')
            except IOError:
                pickle_file=tempfile.NamedTemporaryFile()
                must_copy=True
            pickle.dump(options,pickle_file)
            if must_copy:
                pickle_file.file.flush()
                os.system("sudo cp %s %s" % ( pickle_file.name, os.path.join(ed.options_store_dir,ed.metadata['name'])))
                os.system("sudo chmod a+r %s" % os.path.join(ed.options_store_dir,ed.metadata['name']))
            pickle_file.close()

    else:
        print "\nIncorrect number of arguments: supply one module or file name\n"

        parser.print_help()


