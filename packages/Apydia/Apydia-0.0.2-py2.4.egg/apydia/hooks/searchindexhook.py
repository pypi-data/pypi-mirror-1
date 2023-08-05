"""
    JS search-index generator
"""

import logging

from os import makedirs
from os.path import join, isdir, dirname


__all__ = ["generate_search_index"]

log = logging.getLogger(__name__)


def generate_search_index(project):
    options = project.options
    search_index = []
    for module in project.modules:
        search_index.append(make_entry(module, project))
        for member in module.members:
            search_index.append(make_entry(member, project))
    search_index = sorted(search_index, key=lambda t:t['name'])
    outfile = join(options.destination, "js", "searchindex.js")
    
    log.debug("writing %d entries to \"%s\"", len(search_index), outfile)
    
    if not isdir(dirname(outfile)):
        makedirs(dirname(outfile))
    f = file(outfile, "w")
    try:
        f.writelines(generate_js_file(search_index))
    finally:
        f.close()


def make_entry(entry, project):
    title = project.render_title(entry) or entry.name
    keywords = [entry.pathname]
    keywords.append(entry.represents)
    keywords.append(title)
    return dict(
        name = entry.pathname or entry.name,
        type = entry.represents,
        href = entry.href, 
        keywords = " ".join(keywords).strip(),
        title = title
    )


def generate_js_file(index):
    yield "var apydiaSearchIndex = [\n"
    for entry in index:
        yield "{%s},\n" % ", ".join('%s: "%s"' % p for p in entry.items())
    yield "];\n\n"

