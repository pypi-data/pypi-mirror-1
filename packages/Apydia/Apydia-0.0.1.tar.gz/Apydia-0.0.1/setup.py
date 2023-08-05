try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import os
execfile(os.path.join("apydia", "release.py"))

setup(
    name = "Apydia",
    version = version,
    description = description,
    long_description = long_description,
    author = author,
    author_email = author_email,
    url = url,
    license = "MIT License",
    packages = find_packages(exclude=['ez_setup']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Documentation",
        "Topic :: Internet :: WWW/HTTP"
    ],
    include_package_data = True,
    install_requires = [
        "setuptools >= 0.6c7",
        "Genshi >= 0.4.4",
        "Pygments >= 0.9",
        "BeautifulSoup >= 3.0.4",
    ],
    extras_require = {
        "reST": ["docutils >= 0.4"],
        "Textile": ["textile >= 2.0"],
        "Markdown": ["markdown >= 1.6"],
    },
    entry_points = """
        [console_scripts]
        apydia = apydia.command:main
        
        [distutils.commands]
        apydia = apydia.command:apydia
        
        [apydia.docrenderers]
        plain = apydia.renderers.plaintextrenderer:PlainTextRenderer
        restructuredtext = apydia.renderers.rstrenderer:DocutilsReSTRenderer[reST]
        markdown = apydia.renderers.markdownrenderer:MarkdownRenderer[Markdown]
        textile = apydia.renderers.textilerenderer:TextileRenderer[Textile]
        
        [apydia.post_project_hooks]
        searchindexhook = apydia.hooks.searchindexhook:generate_search_index
        
        [apydia.themes]
        default = apydia.themes.default
        apydia = apydia.themes.apydia
        elixir = apydia.themes.elixir
        
        [pygments.styles]
        apydiadefault = apydia.themes.default:ApydiaDefaultStyle
        apydia = apydia.themes.apydia:ApydiaStyle
        elixir = apydia.themes.elixir:ElixirStyle
    """
)
