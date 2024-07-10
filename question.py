class Question:
    class TimeFilter:
        def __init__(self, year):
            self.year = year

    def __init__(self, id, text):
        self.id = id
        self.text = text
        self.syntax = None
        self.syntax_root = None

    def __str__(self):
        return self.text

    def is_valid(self):
        if self.text == "":
            return False
        return True

    def set_syntax(self, syntax):
        self.syntax = syntax

    def set_syntax_root_index(self, index):
        self.syntax_root = index
