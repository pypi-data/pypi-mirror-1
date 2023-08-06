from paver.runtime import *

try:
    import sphinx
    has_sphinx = True
except ImportError:
    has_sphinx = False

if has_sphinx:
    def _get_paths():
        opts = OPTIONS.sphinx
        docroot = path(opts.get('docroot', 'docs'))
        if not docroot.exists():
            raise BuildFailure("Sphinx documentation root (%s) does not exist."
                               % docroot)
        builddir = docroot / opts.get("builddir", ".build")
        builddir.mkdir()
        srcdir = docroot / opts.get("sourcedir", "")
        if not srcdir.exists():
            raise BuildFailure("Sphinx source file dir (%s) does not exist" 
                                % srcdir)
        htmldir = builddir / "html"
        htmldir.mkdir()
        doctrees = builddir / "doctrees"
        doctrees.mkdir()
        return Bunch(locals())
    
    @target
    @require_keys("sphinx")
    def html():
        """Build HTML documentation using Sphinx. This uses the following
        options in a "sphinx" section of the options.
        
        docroot
          the root under which Sphinx will be working. Default: docs
        builddir
          directory under the docroot where the resulting files are put.
          default: build
        sourcedir
          directory under the docroot for the source files
          default: (empty string)
        """
        paths = _get_paths()
        sphinxopts = ['', '-b', 'html', '-d', paths.doctrees, 
            paths.srcdir, paths.htmldir]
        dry("sphinx-build %s" % (" ".join(sphinxopts),), sphinx.main, sphinxopts)
    
    @target
    @require_keys("sphinx")
    def doc_clean():
        """Clean (delete) the built docs."""
        paths = _get_paths()
        paths.builddir.rmtree()
        paths.builddir.mkdir()
	    