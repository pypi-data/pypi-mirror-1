#coding: utf-8

class DictDataSource(object):
    ''' Absctract base class for dictionary data source.
        Subclasses should make class variables (rules, lemmas, prefixes,
        gramtab, endings, possible_rule_prefixes) accessible through dict
        or list syntax ("duck typing")

        @ivar rules: {paradigm_id->[ (suffix, ancode, prefix) ]}
        @ivar lemmas: {base -> [rule_id]}
        @ivar prefixes: set([prefix])
        @ivar gramtab: {ancode->(type,info,letter)}
        @ivar rule_freq: {paradigm_id->freq}
        @ivar endings: {word_end->{rule_id->(possible_paradigm_ids)}}
        @ivar possible_rule_prefixes: [prefix]
    '''
    def __init__(self):

        # для каждой парадигмы - список правил (приставка, грам. информация,
        # префикс) в формате {paradigm_id->[ (suffix, ancode, prefix) ]}
        self.rules={}

        # для каждой леммы - список номеров парадигм? (способов образования слов),  #TODO: проверить, парадигм ли
        # доступных для данной леммы (основы слова)
        self.lemmas={}

        # фиксированые префиксы
        self.prefixes=set()

        # для каждого возможного 5 буквенного окончания - словарь, в котором
        # ключи - номера возможных парадигм, а значения - номера возможных
        # правил
        self.endings = {}

        # грамматическая информация: словарь, ключи которого - индексы грам.
        # информации (анкоды), значения - кортежи
        # (часть речи, информация о грам. форме, какая-то непонятная буква)
        self.gramtab={}

        # набор всех возможных приставок к леммам
        self.possible_rule_prefixes = set()

        # ударения, не используется
        self.accents=[]

        # частоты для правил, используется при подготовке словарей
        self.rule_freq = {}

        # логи работы с оригинальной программой от aot, не используется
        self.logs=[]

    def load(self):
        """ Загрузить данные """
        raise NotImplementedError

    def convert_and_save(self, data_obj):
        """ Взять данные из data_obj (наследник DataDictSource)
            и сохранить из в специфичном для класса формате.
        """
        raise NotImplementedError

    def calculate_rule_freq(self):
        """
        Подсчитать частоту, с которой встречаются различные правила.
        Требуется для предсказателя, чтобы выбирать наиболее распространенные
        варианты.
        """
        for lemma in self.lemmas:
            for paradigm_id in self.lemmas[lemma]:
                self.rule_freq[paradigm_id] = self.rule_freq.get(paradigm_id,0)+1
