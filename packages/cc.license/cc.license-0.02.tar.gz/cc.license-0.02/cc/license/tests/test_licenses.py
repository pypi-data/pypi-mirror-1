
import nose.tools
import cc.license
from cc.license import CCLicenseError

class TestAll:

    def __init__(self):
        self.stdsel = cc.license.selectors.choose('standard')
        self.smpsel = cc.license.selectors.choose('recombo')
        self.pdsel = cc.license.selectors.choose('publicdomain')

    def test_license_class(self):
        stdlic = self.stdsel.by_code('by')
        assert self.stdsel.id == stdlic.license_class
        smplic = self.smpsel.by_code('sampling')
        assert self.smpsel.id == smplic.license_class
        pdlic = self.pdsel.by_code('publicdomain')
        assert self.pdsel.id == pdlic.license_class

    def test_version(self):
        uri = 'http://creativecommons.org/licenses/by-sa/1.0/'
        lic = self.stdsel.by_uri(uri)
        assert lic.version == u'1.0'
        lic2 = self.stdsel.by_code('by')
        assert lic2.version == u'3.0'

    def test_uri(self):
        uri = 'http://creativecommons.org/licenses/by-sa/3.0/'
        lic = self.stdsel.by_uri(uri)
        assert lic.uri == uri
        lic2 = self.stdsel.by_code('by-sa')
        assert lic2.uri == uri

    def test_uri_multiple(self):
        uri = 'http://creativecommons.org/licenses/by-nc-nd/3.0/'
        lic = self.stdsel.by_uri(uri)
        assert lic.uri == uri
        lic2 = self.stdsel.by_uri(uri)
        assert lic == lic2
        assert lic2.uri == uri
        assert lic2 == self.stdsel.by_uri(uri)
        assert lic2 == self.stdsel.by_uri(uri)

    def test_jurisdiction(self):
        lic = self.stdsel.by_code('by-sa')
        assert lic.jurisdiction.title() == 'Unported'
        assert lic.jurisdiction == cc.license.jurisdictions.by_code('')
        lic2 = self.stdsel.by_code('by-nc', jurisdiction='jp')
        assert lic2.jurisdiction.title() == 'Japan'
        assert lic2.jurisdiction == cc.license.jurisdictions.by_code('jp')

    def test_title(self):
        lic = self.stdsel.by_code('by')
        assert lic.title() == lic.title('en')
        assert lic.title('en') == u'Attribution'
        assert lic.title('es') == u'Reconocimiento'
        assert lic.title('de') == u'Namensnennung'

    def test_description(self):
        # has a description
        lic = self.stdsel.by_code('by')
        assert lic.description() == u'You must attribute the\nwork in the manner specified by the author or licensor.'
        assert lic.description('es') == u'El licenciador permite copiar, distribuir y comunicar p\xfablicamente la obra. A cambio, hay que reconocer y citar al autor original.'
        # doesn't have a description
        lic2 = self.stdsel.by_code('by-sa')
        assert lic2.description() == ''

    def test_deprecated(self):
        lic = self.stdsel.by_code('by')
        assert not lic.deprecated
        lic2 = self.smpsel.by_code('sampling')
        assert lic2.deprecated

    def test_license_code(self):
        # TODO make this iterate over all licenses
        for c in ('by', 'by-sa', 'by-nd', 'by-nc', 'by-nc-sa'):
            lic = self.stdsel.by_code(c)
            assert lic.license_code == c
            assert lic.license_code in repr(lic)

    def test_superseded(self):
        lic = self.stdsel.by_code('by', version='1.0')
        assert lic.superseded
        lic2 = self.stdsel.by_code('by', version='3.0')
        assert not lic2.superseded

    def test_current_version(self):
        lic = self.stdsel.by_code('by')
        assert lic.current_version == lic.version
        lic2 = self.stdsel.by_code('by', version='1.0')
        assert lic2.current_version == '3.0'

    def test_permits(self):
        lic = self.stdsel.by_code('by')
        for p in lic.permits:
            assert p.startswith('http://creativecommons.org/ns#')

    def test_requires(self):
        lic = self.stdsel.by_code('by')
        for r in lic.requires:
            assert r.startswith('http://creativecommons.org/ns#')

    def test_prohibits(self):
        lic = self.stdsel.by_code('by')
        for p in lic.prohibits:
            assert p.startswith('http://creativecommons.org/ns#')

    def test_libre(self):
        free = [self.stdsel.by_code('by'), self.stdsel.by_code('by-sa'),
                self.pdsel.by_code('publicdomain')]
        unfree = [ self.stdsel.by_code(c) for c in ('by-nc', 'by-nc-sa') ]
        for c in ('sampling', 'nc-sampling+', 'sampling+'):
            unfree.append(self.smpsel.by_code(c))
        for f in free:
            assert f.libre
        for u in unfree:
            assert not u.libre

    def test_logo(self):
        base = 'http://i.creativecommons.org/l/'
        by = self.stdsel.by_code('by')
        assert type(by.logo) is str
        assert by.logo.startswith(base)
        smp = self.smpsel.by_code('sampling+')
        assert type(smp.logo) is str
        assert smp.logo.startswith(base)
        by_jp = self.stdsel.by_code('by', jurisdiction='jp')
        assert 'jp' in by_jp.logo

    def test_has_license(self):
        std = 'http://creativecommons.org/licenses/by/3.0/'
        smp = 'http://creativecommons.org/licenses/sampling+/1.0/'
        pd = 'http://creativecommons.org/licenses/publicdomain/'
        assert self.stdsel.has_license(std)
        assert not self.stdsel.has_license(pd)
        assert self.smpsel.has_license(smp)
        assert not self.smpsel.has_license(std)
        assert self.pdsel.has_license(pd)
        assert not self.pdsel.has_license(smp)


class TestStandard:

    def setUp(self):
        self.selector = cc.license.selectors.choose('standard')

    def test_bysa_same(self):
        lic1 = self.selector.by_code('by-sa')
        lic2 = self.selector.by_code('by-sa')
        assert lic1 == lic2
        assert lic1 is lic2 # For "efficiency", why not?

    def test_bysa_generic(self):
        lic = self.selector.by_code('by-sa')
        assert lic.jurisdiction.title() == 'Unported'
        # assert_true(lic.libre) # FIXME: Should this be here?

    def test_bysa_us(self):
        # nonexistent license raises an error
        nose.tools.assert_raises(CCLicenseError, self.selector.by_code,
                    'by-sa', jurisdiction='us', version='1.0')

        lic = self.selector.by_code('by-sa', jurisdiction='us', version='3.0')
        assert lic.jurisdiction.code == 'us'
        # assert_true(lic.libre) # FIXME: Should this be here?

        # Now, test automatic version selection - but FIXME
        # do that later.

class TestSampling:

    def setUp(self):
        self.selector = cc.license.selectors.choose('recombo')

    def test_title(self):
        lic = self.selector.by_code('sampling')
        assert lic.title() == 'Sampling'

class TestPublicDomain:

    def setUp(self):
        self.selector = cc.license.selectors.choose('publicdomain')
        self.lic = self.selector.by_code('publicdomain')

    def test_title(self):
        assert self.lic.title() == 'Public Domain'

    def test_title_default(self):
        assert self.lic.title() == self.lic.title('en')

class TestCustomization:

    def __init__(self):
        std = cc.license.selectors.choose('standard')
        smp = cc.license.selectors.choose('recombo')
        pd = cc.license.selectors.choose('publicdomain')
        lics = []
        lics.append(std.by_code('by'))
        lics.append(std.by_code('by-nc-nd'))
        lics.append(std.by_code('by-sa', jurisdiction='jp'))
        lics.append(smp.by_code('sampling'))
        lics.append(smp.by_code('nc-sampling+', jurisdiction='tw'))
        lics.append(pd.by_code('publicdomain'))
        self.licenses = lics

    def test_repr(self):
        for l in self.licenses:
            r = repr(l)
            assert l.uri in r
            assert 'License' in r
            assert r.startswith('<')
            assert r.endswith('>')

    def test_str(self):
        for l in self.licenses:
            s = str(l)
            assert l.title() in s
            assert l.version in s
            assert l.jurisdiction.title() in s
