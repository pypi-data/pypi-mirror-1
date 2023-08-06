"""Tests for Jurisdiction class and other functionality related
   to jurisdictions."""

import cc.license
from cc.license.lib.exceptions import CCLicenseError
import nose.tools

# TODO: additional tests exercising the output
def test_jurisdictions():
    jurisdictions = cc.license.jurisdictions.list()
    for j in jurisdictions:
        assert type(j) == cc.license.Jurisdiction

def test_jurisdiction_codes():
    codes = cc.license.jurisdictions.list_codes()
    # scotland is in there, and it's the only one that isn't 2 letters
    assert 'scotland' in codes
    codes.remove('scotland')
    # excepting the empty string (default jurisdiction) of course
    assert '' in codes
    codes.remove('')
    # they are all strings of length 2
    for c in codes:
        assert type(c) == str
        assert len(c) == 2
    # test a few big jurisdictions
    for k in ('us', 'uk', 'fr', 'de', 'jp', 'ca'):
        print k 
        assert k in codes

def test_commutativity():
    codes = cc.license.jurisdictions.list_codes()
    for uri in cc.license.jurisdictions.list_uris():
        assert cc.license.jurisdictions.uri2code(uri) in codes

def test_code_constructor():
    for k in ('us', 'uk', 'fr', 'de', 'jp', 'ca'):
        j = cc.license.jurisdictions.by_code(k)
        assert type(j) == cc.license.Jurisdiction

def test_unported():
    j = cc.license.jurisdictions.by_code('')
    assert j == cc.license.Jurisdiction('')
    assert j.title() == 'Unported'

def test_equality():
    codes = ('', 'jp', 'us')
    one, two, three = ( cc.license.jurisdictions.by_code(c) for c in codes )
    four, five, six = ( cc.license.jurisdictions.by_code(c) for c in codes )
    assert one == one
    assert not (one != one)
    assert one == four
    assert not (one != four)
    assert one != two
    assert two == five
    assert three != four
    assert three == six
    assert not (two == three)
    assert not (five == six)

class TestJurisdictions:

    def __init__(self):
        self.langs = ('fr', 'ja', 'de', 'en')
        self.mx = cc.license.Jurisdiction(
                     'http://creativecommons.org/international/mx/')

    def test_jurisdiction(self):
        assert 'creativecommons.org.mx' in self.mx.local_url
        assert self.mx.code == 'mx'
        assert self.mx.launched
        assert self.mx.id.endswith('mx/')

    def test_unported(self):
        j = cc.license.Jurisdiction('')
        assert j.code == ''
        assert j.id == ''
        assert j.local_url == '' #XXX check me!
        assert j.launched

    def test_titles(self):
        for t in self.langs:
            title = self.mx.title(t)
            assert type(title) == unicode
            assert len(title) != 0

    def test_title_fails(self):
        nose.tools.assert_raises(CCLicenseError,
                                 self.mx.title, 'roflcopter')

    def test_title_default(self):
        assert self.mx.title() == self.mx.title('en')

    def test_constructor_fails(self):
        nose.tools.assert_raises(CCLicenseError,
                             cc.license.Jurisdiction, 'lollerskates')
