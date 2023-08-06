"""The namespace for the pavement to run in, also includes default targets."""

from paver.runtime import *
from paver import setuputils

@target
def help():
    """Displays the list of commands and the details."""
    targetnames = sorted(TARGETS.keys())
    for targetname in targetnames:
        target = TARGETS[targetname]
        info("  %-15s - %s" % (targetname, target.help))

_docsdir = path(__file__).parent / "docs"
if _docsdir.exists():
    @target
    def paverdocs():
        """Open your web browser and display Paver's documentation."""
        import webbrowser
        webbrowser.open("file://" + (_docsdir.abspath() / 'index.html'))
        