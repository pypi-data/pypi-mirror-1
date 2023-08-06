try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(name='Unidecode',
      version='0.04.1',
      description='US-ASCII transliterations of Unicode text',
      url='http://www.tablix.org/~avian/blog/archives/2009/01/unicode_transliteration_in_python/',
      long_description="""
Unidecode
=========

ASCII transliterations of Unicode text

Example Use
-----------

::

	from unidecode import unidecode
	print unidecode(u"\u5317\u4EB0")

	# That prints: Bei Jing 

Description
-----------

It often happens that you have non-Roman text data in Unicode, but
you can't display it -- usually because you're trying to show it
to a user via an application that doesn't support Unicode, or
because the fonts you need aren't accessible. You could represent
the Unicode characters as "???????" or "\15BA\15A0\1610...", but
that's nearly useless to the user who actually wants to read what
the text says.

What Unidecode provides is a function, 'unidecode(...)' that
takes Unicode data and tries to represent it in ASCII characters 
(i.e., the universally displayable characters between 0x00 and 0x7F). 
The representation is almost always an attempt at *transliteration* 
-- i.e., conveying, in Roman letters, the pronunciation expressed by 
the text in some other writing system. (See the example above)

This is a Python port of Text::Unidecode Perl module by 
Sean M. Burke <sburke@cpan.org>.
      """,
      author='Tomaz Solc',
      author_email='tomaz.solc@tablix.org',

      packages = [ 'unidecode' ],

      provides = [ 'unidecode' ],
)
