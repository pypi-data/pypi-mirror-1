from setuptools import setup
setup(
    name = "Phon",
    description = "Unix filter for naive phonological analysis of words in wordlists.",
    version = "0.1a3",
    scripts = ['phon'],
    author = 'kaleissin',
    author_email = 'kaleissin@gmail.com',
    license = 'MIT',
    keywords = "phonology linguistics analysis unix",
    long_description = """Given a list of words, one word per line, on
stdin, phon will dump onsets, codas, consonants between vowels
(middles) and all consonant groupings (pieces)."""
)

