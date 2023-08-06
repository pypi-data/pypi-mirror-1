
import nose.tools
import cc.license
from cc.license.lib.rdf_helper import questions_root as root
from cc.license.lib.exceptions import CCLicenseError

class TestStandard:

    def __init__(self):
        self.qc = cc.license.Question(root, 'standard', 'commercial')
        self.qd = cc.license.Question(root, 'standard', 'derivatives')
        self.qj = cc.license.Question(root, 'standard', 'jurisdiction')
        self.all = [self.qc, self.qd, self.qj]

    def test_id(self):
        assert self.qc.id == 'commercial'
        assert self.qd.id == 'derivatives'
        assert self.qj.id == 'jurisdiction'

    def test_constructor_fails(self):
        nose.tools.assert_raises(CCLicenseError, cc.license.Question,
                             root, 'lolcats', 'commercial')
        nose.tools.assert_raises(CCLicenseError, cc.license.Question,
                             root, 'standard', 'qwertyitis')
        nose.tools.assert_raises(CCLicenseError, cc.license.Question,
                             root, 'azerbaijan', 'icanhascheezburger')
    
    def test_label(self):
        assert self.qd.label() == 'Allow modifications of your work?'
        assert self.qd.label('es') == \
               u'\xbfQuiere permitir modificaciones de su obra?'

    def test_label_default(self):
        for q in self.all:
            assert q.label() == q.label('en')
            assert q.label() != q.label('de')

    def test_description_default(self):
        for q in self.all:
            assert q.description() == q.description('en')
            assert q.description() != q.description('ja')

    def test_answers(self):
        for q in self.all:
            answers = q.answers()
            for answer in answers:
                assert type(answer) is tuple
                assert type(answer[0]) is str
                assert type(answer[1]) is str
            answers2 = q.answers('ja')
            for i in range(len(answers)):
                assert answers[i][1] == answers2[i][1]

    def test_answers_default(self):
        assert self.qd.answers() == self.qd.answers('en')
        assert self.qd.answers() != self.qd.answers('es')

class TestSampling:
    pass

class TestPublicDomain:
    pass
