from subdist import substring, get_score

def test_empty_haystack():
    d = substring(u"spam", u"")
    assert d == 4, d

class TestQuickBrownFox:
    def setup(self):
        self.haystack = u"the quick brown fox jumped over the lazy dogs"
        
    def test_quick(self):
        d = substring(u"quick", self.haystack)
        assert d == 0, d

    def test_quickly(self):
        d = substring(u"quickly", self.haystack)
        assert d == 2, d

    def test_brown(self):
        d = substring(u"brown", self.haystack)
        assert d == 0, d
        
    def test_Brown(self):
        d = substring(u"Brown", self.haystack)
        assert d == 1, d
        
    def test_fox(self):
        d = substring(u"fox", self.haystack)
        assert d == 0, d
        
    def test_foxy(self):
        d = substring(u"foxy", self.haystack)
        assert d == 1, d

    def test_jumped(self):
        d = substring(u"jumped", self.haystack)
        assert d == 0, d

    def test_jumps(self):
        d = substring(u"jumps", self.haystack)
        assert d == 1, d

    def test_over(self):
        d = substring(u"over", self.haystack)
        assert d == 0, d

    def test_oven(self):
        d = substring(u"oven", self.haystack)
        assert d == 1, d

    def test_lazy(self):
        d = substring(u"lazy", self.haystack)
        assert d == 0, d

    def test_dog(self):
        d = substring(u"dog", self.haystack)
        assert d == 0, d

    def test_dogs(self):
        d = substring(u"dogs", self.haystack)
        assert d == 0, d

    def test_SPAM(self):
        d = substring(u"SPAM", self.haystack)
        assert d == 4, d

    def test_empty(self):
        d = substring(u"", self.haystack)
        assert d == 0, d

class TestGetScore:
    def setup(self):
        self.haystack = u"the quick brown fox jumped over the lazy dogs"

    def test_quick(self):
        score = get_score(u"quick", self.haystack)
        assert score == 1.0, score

    def test_quickly(self):
        score = get_score(u"quickly", self.haystack)
        assert score == 5.0 / 7.0, score
