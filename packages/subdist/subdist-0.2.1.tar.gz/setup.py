from distutils.core import setup, Extension

subdist_module = Extension('subdist',
                    sources = ['subdist.c'])

description = """A C extension that uses a modified version 
of the Levenshtein distance algorithm to calculate fuzzy matches 
for substrings.

Usage:
import subdist
distance = subdist.substring(u"spam", u"I sought only ham.")
score = subdist.get_score(u"ham", u"But I found only spam")

MIT License
"""

setup (name = 'subdist',
       version = '0.2.1',
       description = 'Substring edit distance',
       long_description = description,
        author = "Ryan Ginstrom",
        author_email = "software@ginstrom.com",
        download_url = "http://ginstrom.com/code/subdist-0.2.tar.gz",
        url="http://www.ginstrom.com/code/subdist.html",
        license="MIT",
       ext_modules = [subdist_module])
      