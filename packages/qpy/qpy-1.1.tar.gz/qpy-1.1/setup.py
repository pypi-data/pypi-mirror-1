"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/setup.py $
$Id: setup.py 27631 2005-10-28 13:47:01Z dbinger $
"""
from distutils.core import setup
from distutils.command.build_py import build_py
from distutils.extension import Extension
from glob import glob
import os

class qpy_build_py(build_py):

    def find_package_modules(self, package, package_dir):
        self.check_package(package, package_dir)
        module_files = (glob(os.path.join(package_dir, "*.py")) +
                        glob(os.path.join(package_dir, "*.qpy")))
        modules = []
        setup_script = os.path.abspath(self.distribution.script_name)
        for f in module_files:
            abs_f = os.path.abspath(f)
            module = os.path.splitext(os.path.basename(f))[0]
            modules.append((package, module, f))
        return modules

    def build_module(self, module, module_file, package):
        if type(package) is str:
            package = package.split('.')
        elif type(package) not in (list, tuple):
            raise TypeError, \
                  "'package' must be a string (dot-separated), list, or tuple"
        # Now put the module source file into the "build" area.
        outfile = self.get_module_outfile(self.build_lib, package, module)
        if module_file.endswith(".qpy"): 
            outfile = outfile[0:outfile.rfind('.')] + ".qpy"
        dir = os.path.dirname(outfile)
        self.mkpath(dir)
        return self.copy_file(module_file, outfile, preserve_mode=0)


if __name__ == '__main__':
    setup(
        name="qpy",
        version="1.1",
        description="unicode/html content in functions",
        author="CNRI",
        author_email="webmaster@mems-exchange.org",
        url="http://www.mems-exchange.org/software/qpy/",
        license="see LICENSE.txt",
        package_dir=dict(qpy=os.curdir),
        packages=['qpy'],
        scripts=['qpcheck.py', 'qpyrun.py'],
        ext_modules=[Extension(name="qpy.c8", sources=["c8.c"])],
        cmdclass= {'build_py': qpy_build_py},
        long_description=(
        "Qpy provides a convenient mechanism for generating safely-quoted html "
        "text from python code.  It does this by implementing a quoted-string "
        "data type and a modification of the python compiler.  (This main idea "
        "comes from Quixote's htmltext/PTL.)")
        )
