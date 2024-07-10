import spacy


class SyntaxParser:
    LANGUAGE = "en_core_web_sm"

    def __init__(self):
        self.spacy = spacy.load(SyntaxParser.LANGUAGE)

    def parse(self, question):
        question.set_syntax(self.spacy(question.text))

        SyntaxParser.find_root(question)

    @staticmethod
    def find_root(question):
        for token in question.syntax:
            if token.dep_ == "ROOT":
                question.set_syntax_root_index(token.i)

                return

