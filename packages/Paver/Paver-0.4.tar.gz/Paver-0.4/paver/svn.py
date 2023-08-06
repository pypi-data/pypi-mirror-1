"""Convenience functions for working with svn.

This module does not include any targets, only functions.

At this point, these functions do not use any kind of library. They require
the svn binary on the path."""

from paver.runtime import sh, Bunch

def _format_revision(revision):
    if revision:
        revision = "-r %s " % (revision)
    return revision
    
def checkout(url, dest, revision=""):
    """Checks out the specified URL to the given destination."""
    revision = _format_revision(revision)
    sh("svn co %s%s %s" % (revision, url, dest))

def update(path="", revision=""):
    """Run an svn update on the given path."""
    revision = _format_revision(revision)
    command = "svn up %s" % revision
    if path:
        command += path
    sh(command)

def info(path=""):
    """Retrieves the svn info for the path and returns a dictionary of 
    the values. Names are normalized to lower case with spaces converted
    to underscores."""
    output = sh("svn info %s" % path, capture=True)
    if not output:
        return Bunch()
    lines = output.splitlines()
    data = Bunch()
    for line in lines:
        colon = line.find(":")
        if colon == -1:
            continue
        key = line[:colon].lower().replace(" ", "_")
        value = line[colon+2:]
        data[key] = value
    return data
    