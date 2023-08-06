#coding: utf-8
import unittest
import os

from pymorphy.morph import get_morph
from pymorphy.morph import GramForm


DICT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         '..', 'dicts', 'converted'))

class GramFormTest(unittest.TestCase):

    def testFromStr(self):
        form = GramForm(u'мн,рд')
        self.assertTrue(u'рд' in form.form)
        self.assertTrue(u'мн' in form.form)

    def testFormChange(self):
        form = GramForm(u'мн,рд,мр')
        form.update(u'дт')
        self.assertTrue(u'дт' in form.form)
        self.assertTrue(u'мн' in form.form)
        self.assertFalse(u'рд' in form.form)

    def testFormMultiChange(self):
        form = GramForm(u'мн,рд,мр')
        form.update(u'дт,ед')
        self.assertTrue(u'дт' in form.form)
        self.assertTrue(u'ед' in form.form)
        self.assertFalse(u'рд' in form.form)
        self.assertFalse(u'мн' in form.form)

    def testFormStr(self):
        form = GramForm(u'мр,мн,рд')
        self.assertTrue(form.get_form_string().count(u'мр') == 1)
        self.assertTrue(form.get_form_string().count(u'мн') == 1)
        self.assertTrue(form.get_form_string().count(u'рд') == 1)
        self.assertTrue(len(form.get_form_string()) == (2*3)+2)
        form.update(u'дт')
        self.assertTrue(form.get_form_string().count(u'мр') == 1)
        self.assertTrue(form.get_form_string().count(u'мн') == 1)
        self.assertTrue(form.get_form_string().count(u'дт') == 1)
        self.assertTrue(len(form.get_form_string()) == (2*3)+2)

    def testMatch(self):
        form = GramForm(u"мр,ед,имя")
        self.assertTrue(form.match(GramForm(u"мр")))
        self.assertTrue(form.match(GramForm(u"ед,мр")))

    def testMatch2(self):
        form = GramForm(u"мр,ед,имя")
        self.assertFalse(form.match(GramForm(u"мр,!имя")))
        self.assertTrue(form.match(GramForm(u"ед,!тв")))


class TestMorph(unittest.TestCase):
    morph_ru = get_morph(os.path.join(DICT_PATH, 'ru'))
    morph_en = get_morph(os.path.join(DICT_PATH, 'en'))

    def check_norm(self, input, output):
        norm_forms = self.morph_ru.normalize(input)
        correct_norm_forms = set(output)

        msg = u"[%s] != [%s]" % (u", ".join(norm_forms), u", ".join(correct_norm_forms))
        self.assertEqual(norm_forms, correct_norm_forms, msg)

    def check_norm_en(self, input, output):
        self.assertEqual(self.morph_en.normalize(input), set(output))

    def testNormalize(self):
        self.check_norm(u'КОШКА', [u'КОШКА'])
        self.check_norm(u'КОШКЕ', [u'КОШКА'])
        self.check_norm(u'СТАЛИ', [u'СТАЛЬ', u'СТАТЬ'])

        self.check_norm_en('SOLD', ['SELL'])
        self.check_norm_en('COMPUTERS', ['COMPUTER'])

    def testGlobalPrefixNormalize(self):
        self.check_norm(u'ПСЕВДОКОШКА', [u'ПСЕВДОКОШКА'])
        self.check_norm(u'ПСЕВДОКОШКОЙ', [u'ПСЕВДОКОШКА'])

    def testRulePrefixNormalize(self):
        self.check_norm(u'НАИСТАРЕЙШИЙ', [u'СТАРЫЙ'])
        self.check_norm(u'СВЕРХНАИСТАРЕЙШИЙ', [u'СВЕРХСТАРЫЙ'])
        self.check_norm(u'СВЕРХНАИСТАРЕЙШИЙ', [u'СВЕРХСТАРЫЙ'])
        self.check_norm(u'КВАЗИПСЕВДОНАИСТАРЕЙШЕГО', [u'КВАЗИПСЕВДОСТАРЫЙ'])
        self.check_norm(u'НЕБЕСКОНЕЧЕН', [u'НЕБЕСКОНЕЧНЫЙ'])

    def testPrefixPredict(self):
        self.check_norm(u'МЕГАКОТУ', [u'МЕГАКОТ'])
        self.check_norm(u'МЕГАСВЕРХНАИСТАРЕЙШЕМУ', [u'МЕГАСВЕРХСТАРЫЙ'])

    def testEEbug(self):
        self.check_norm(u'КОТЕНОК', [u'КОТЕНОК'])
        self.check_norm(u'ТЯЖЕЛЫЙ', [u'ТЯЖЕЛЫЙ'])
        self.check_norm(u'ЛЕГОК', [u'ЛЕГКИЙ'])
        # fix dict for this? done.
        # should fail if dictionaries are converted using strip_EE=False option

    def testPronouns(self):

        self.check_norm_en(u'SHE', [u'SHE'])
        self.check_norm_en(u'I', [u'I'])
        self.check_norm_en(u'ME', [u'I'])

        self.check_norm(u'ОНА', [u'ОНА'])
        self.check_norm(u'ЕЙ', [u'ОНА'])
        self.check_norm(u'Я', [u'Я'])
        self.check_norm(u'МНЕ', [u'Я'])
        self.check_norm(u'ЕГО', [u'ОН', u'ОНО'])
        self.check_norm(u'ЕМУ', [u'ОН', u'ОНО'])

    def testNoBase(self):
        self.check_norm(u'НАИНЕВЕРОЯТНЕЙШИЙ', [u'ВЕРОЯТНЫЙ'])
        self.check_norm(u'ЛУЧШИЙ', [u'ХОРОШИЙ'])
        self.check_norm(u'НАИЛУЧШИЙ', [u'ХОРОШИЙ'])
        self.check_norm(u'ЧЕЛОВЕК', [u'ЧЕЛОВЕК'])
        self.check_norm(u'ЛЮДИ', [u'ЧЕЛОВЕК'])

    def testPredict(self):
        self.check_norm(u'ТРИЖДЫЧЕРЕЗПИЛЮЛЮОКНАМИ', [u'ТРИЖДЫЧЕРЕЗПИЛЮЛЮОКНА'])
        self.check_norm(u'РАЗКВАКАЛИСЬ',[u'РАЗКВАКАТЬСЯ'])
        self.check_norm(u'КАШИВАРНЕЕ', [u'КАШИВАРНЫЙ', u'КАШИВАРНАЯ', u'КАШИВАРНОЕ'])
        self.check_norm(u'ДЕПЫРТАМЕНТОВ',[u'ДЕПЫРТАМЕНТ'])
        self.check_norm(u'ИЗМОХРАТИЛСЯ',[u'ИЗМОХРАТИТЬСЯ'])

    def testNoProdClassesInPrediction(self):
        self.check_norm(u'БУТЯВКОЙ',[u'БУТЯВКА']) # и никаких местоимений!
        self.check_norm(u'САПАЮТ',[u'САПАТЬ']) # и никаких местоимений!

    def testFemale(self):
        self.check_norm(u'КЛЮЕВУ', [u'КЛЮЕВ', u'КЛЮЕВА'])
        self.check_norm(u'КЛЮЕВА', [u'КЛЮЕВА', u'КЛЮЕВ'])

    def testVerbs(self):
        self.check_norm(u'ГУЛЯЛ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯЛА', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯЕТ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯЮТ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯЛИ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯТЬ', [u'ГУЛЯТЬ'])

    def testVerbProducts(self):
        self.check_norm(u'ГУЛЯЮЩИЙ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯВШИ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯЯ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ГУЛЯЮЩАЯ', [u'ГУЛЯТЬ'])
        self.check_norm(u'ЗАГУЛЯВШИЙ', [u'ЗАГУЛЯТЬ'])

    def testKeepGender(self):
        self.check_norm(u'КРАСИВЫЙ', [u'КРАСИВЫЙ'])
        self.check_norm(u'КРАСИВАЯ', [u'КРАСИВАЯ'])
        self.check_norm(u'КРАСИВОМУ', [u'КРАСИВЫЙ', u'КРАСИВОЕ'])
        self.check_norm(u'КРАСИВЫЕ', [u'КРАСИВЫЙ', u'КРАСИВАЯ', u'КРАСИВОЕ'])


class TestPluraliseRu(unittest.TestCase):
    morph = get_morph(os.path.join(DICT_PATH, 'ru'))

    def assert_plural(self, word, plural, *args, **kwargs):
        morphed_word = self.morph.pluralize_ru(word, *args, **kwargs)
        self.assertEqual(morphed_word, plural, u"%s != %s" % (morphed_word, plural))

# работающие тесты ============================
    def testNouns(self):
        self.assert_plural(u'ГОРОД', u'ГОРОДА')
        self.assert_plural(u'СТАЛЬ', u'СТАЛИ')
        self.assert_plural(u'СТАЛЕВАРОМ', u'СТАЛЕВАРАМИ')

    def testPredictorNouns(self):
        self.assert_plural(u'БУТЯВКОЙ', u'БУТЯВКАМИ')

    def testVerbs(self):
        self.assert_plural(u'ГУЛЯЛ', u'ГУЛЯЛИ')
        self.assert_plural(u'ГУЛЯЛА', u'ГУЛЯЛИ')
        self.assert_plural(u'РАСПРЫГИВАЕТСЯ', u'РАСПРЫГИВАЮТСЯ')

    def testPrefix(self):
        self.assert_plural(u'СУПЕРКОТ', u'СУПЕРКОТЫ')

    def testPredictBySuffix(self):
        self.assert_plural(u'ДЕПЫРТАМЕНТ', u'ДЕПЫРТАМЕНТЫ')
        self.assert_plural(u'ХАБР', u'ХАБРЫ')

    def testInvalidWord(self):
        self.assert_plural(u'123', u'123')

    def testInvalidGraminfo(self):
        self.assert_plural(u'НАЧАЛО', u'НАЧАЛА', gram_class=u'С')



class TestInflectRu(unittest.TestCase):
    morph = get_morph(os.path.join(DICT_PATH, 'ru'))

    def assert_inflect(self, word, form, result, *args, **kwargs):
        morphed_word = self.morph.inflect_ru(word, form, *args, **kwargs)
        self.assertEqual(morphed_word, result, u"%s != %s" % (morphed_word, result))

    def testInflect(self):
        self.assert_inflect(u"СУСЛИКОВ", u"дт", u"СУСЛИКАМ")
        self.assert_inflect(u"СУСЛИК", u"дт", u"СУСЛИКУ")
        self.assert_inflect(u"СУСЛИКА", u"дт", u"СУСЛИКУ")
        self.assert_inflect(u"СУСЛИК", u"мн,дт", u"СУСЛИКАМ")

    def testVerbs(self):
        self.assert_inflect(u"ГУЛЯЮ", u"прш", u"ГУЛЯЛ")
        self.assert_inflect(u"ГУЛЯЛ", u"нст", u"ГУЛЯЮ")


class TestPluralizeInflected(unittest.TestCase):
    morph = get_morph(os.path.join(DICT_PATH, 'ru'))

    def assert_morph(self, word, count, result, *args, **kwargs):
        morphed_word = self.morph.pluralize_inflected_ru(word, count, *args, **kwargs)
        self.assertEqual(morphed_word, result, u"%s != %s" % (morphed_word, result))

    def testParrots(self):
        self.assert_morph(u"ПОПУГАЙ", 1, u"ПОПУГАЙ")
        self.assert_morph(u"ПОПУГАЙ", 2, u"ПОПУГАЯ")
        self.assert_morph(u"ПОПУГАЙ", 3, u"ПОПУГАЯ")
        self.assert_morph(u"ПОПУГАЙ", 4, u"ПОПУГАЯ")
        self.assert_morph(u"ПОПУГАЙ", 5, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 7, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 9, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 0, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 10, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 11, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 12, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 15, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 19, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 21, u"ПОПУГАЙ")
        self.assert_morph(u"ПОПУГАЙ", 32, u"ПОПУГАЯ")
        self.assert_morph(u"ПОПУГАЙ", 38, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 232, u"ПОПУГАЯ")
        self.assert_morph(u"ПОПУГАЙ", 111, u"ПОПУГАЕВ")
        self.assert_morph(u"ПОПУГАЙ", 101, u"ПОПУГАЙ")

    def testButyavka(self):
        self.assert_morph(u"БУТЯВКА", 1, u"БУТЯВКА")
        self.assert_morph(u"БУТЯВКА", 2, u"БУТЯВКИ")
        self.assert_morph(u"БУТЯВКА", 5, u"БУТЯВОК")
