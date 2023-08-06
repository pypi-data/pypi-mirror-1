
from zc.recipe.cmmi import Recipe as BaseRecipe
from zc.recipe.cmmi import system
import elementtree
import glob
import os

class Recipe(BaseRecipe):

    def cmmi(self, dest):
        """Do the 'configure; make; make install' command sequence.

        When this is called, the current working directory is the
        source directory.  The 'dest' parameter specifies the
        installation prefix.
        """
        options = self.configure_options
        if options is None:
            options = '--prefix=%s' % dest
        if self.extra_options:
            options += ' %s' % self.extra_options
        system("%s %s" % (self.configure_cmd, options))

        # Add the path to elementtree to os.environ
        old_path = os.environ.get('PYTHONPATH')
        add_path = os.path.dirname(os.path.dirname(elementtree.__file__))
        if old_path:
            new_path = '%s:%s' % (add_path, old_path)
        else:
            new_path = add_path
        os.environ['PYTHONPATH'] = new_path
        try:
            # build it
            system("make")
            system("make install")
        finally:
            del os.environ['PYTHONPATH']
            if old_path:
                os.environ['PYTHONPATH'] = old_path

        # make a fake egg from the installed Python code
        dirs = glob.glob(os.path.join(dest, 'lib', 'python*', 'site-packages'))
        if len(dirs) != 1:
            raise AssertionError("Expected one site-packages directory, "
                "but got %s" % repr(dirs))
        d = dirs[0]
        f = open(os.path.join(d, 'lasso.egg-info'), 'w')
        f.write('Metadata-Version: 1.0\nName: lasso\nVersion: 0\n')
        f.close()

        f = open(os.path.join(
            self.buildout['buildout']['develop-eggs-directory'],
            'lasso.egg-link'), 'w')
        f.write('%s\n' % d)
        f.close()
