import paver.sphinxdoc

from metainfo import setup_meta

options(
    setup = setup_meta,
    sphinx=Bunch(
        builddir="build",
        sourcedir="source"
    )
)

@target
@needs('paver.sphinxdoc.html')
def html():
    """Build Paver's documentation and install it into paver/docs"""
    builtdocs = path("docs") / options.sphinx.builddir / "html"
    destdir = path("paver") / "docs"
    destdir.rmtree()
    builtdocs.move(destdir)

