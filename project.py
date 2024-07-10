import sys
import requests
import untangle
import itertools

from syntaxparser import SyntaxParser
from question import Question


def printInstructions():
    print("Using \"ctrl-Z\" to exit the program does not free the memory of the program instance. "
          "Use \"ctrl-C\" instead.")


def getCodesFromString(word, isProperty=False):
    url = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbsearchentities',
        'language': 'en',
        'format': 'json'
    }

    codes = []

    if isProperty:  # returns property codes "Pxx"
        params['type'] = 'property'

    params['search'] = word
    json = requests.get(url, params).json()

    for result in json['search']:
        codes.append("{}".format(result['id']))

    return codes


def beginningOfQuery():
    return '''
    SELECT ?itemLabel WHERE {
        SERVICE wikibase:label {bd:serviceParam wikibase:language "en".}
    '''


def endOfQuery():
    return '''
    }
    '''


def makeSimpleLine(predicateCode, objectCode):
    return '''
    wd:''' + objectCode + ''' wdt:''' + predicateCode + ''' ?item.
    '''


def constructSimpleQuery(predicateCode, objectCode, extraLines=""):
    query = beginningOfQuery()
    query += makeSimpleLine(predicateCode, objectCode)

    return query + extraLines + endOfQuery()


def extractAnswerListFromResult(result):
    if result.split()[0] == "SPARQL-QUERY:":
        # print("Query Timeout Exception Caught.")
        return []

    results = untangle.parse(result)

    answers = []
    for result in results.sparql.results.children:
        if len(result.children) < 1:
            continue
        
        if result.binding.literal["xml:lang"] is None:
            if result.binding.literal.cdata[0] == 'Q':
                continue

        if result.binding.literal.cdata in answers:
            continue

        answers.append(result.binding.literal.cdata)
    return answers


def getSimpleAnswer(predicateCode, objectCode, extraLines=""):
    query = constructSimpleQuery(predicateCode, objectCode, extraLines)
    request = requests.get("https://query.wikidata.org/sparql?query=" + query)

    return extractAnswerListFromResult(request.text)


def createAllObjectCombinations(objectList):
    return list(itertools.product(*objectList))


def writeAndPrintAnswers(answers):
    res = question.id

    for answer in answers:  # print all answers of this query
        res += "\t" + answer

    with open(answerFile, "a+") as file:
        file.write(res + "\n")

    print(res)


def areValid(answers):
    if len(answers) > 0:
        return True

    return False


def getXOfY(X, Y):
    predicates = getCodesFromString(X, True)
    objectList = getCodesFromString(Y)

    # print(predicates)
    # print(objectList)

    for obj in objectList:
        for predicate in predicates:
            answers = getSimpleAnswer(predicate, obj)

            if areValid(answers):
                writeAndPrintAnswers(answers)
                return True  # if the query returned an answer, stop searching

    return False


def getCorrectChildToken(token):
    if token.dep_ == "prep":
        for child in token.children:
            if child.tag_ in ("WP", "WDT"):
                return None
            return child
        return None
    return token


def standardStrategy(doc, rootIndex):  # give me X of Y / Y's X
    rootToken = doc[rootIndex]
    for XToken in rootToken.subtree:
        # print('\t'.join((XToken.text, XToken.lemma_, XToken.pos_, XToken.tag_, XToken.dep_, XToken.head.lemma_)))
        if XToken.dep_ in ("nsubj", "attr", "dobj", "ccomp") and XToken.lemma_ != "-PRON-":  # X is one of the root's children with one of these dependencies
            X = XToken.text

            for YToken in XToken.children:
                # print('\t'.join(('\t', YToken.text, YToken.lemma_, YToken.pos_, YToken.tag_, YToken.dep_, YToken.head.lemma_)))
                if YToken.dep_ in ("poss", "prep"):  # Y is a (grand)child of X
                    YToken = getCorrectChildToken(YToken)
                    if YToken is None:
                        continue

                    Y = YToken.text
                    if getXOfY(X, Y):
                        return True

    return False


if __name__ == '__main__':
    printInstructions()
    answerFile = "answers.txt"

    syntax_parser = SyntaxParser()

    with open(answerFile, "w") as file:
        file.write("")

    for line in sys.stdin:
        if line.strip() == "":  # empty line cannot be parsed, causes crashes if not skipped
            continue

        lines = line.split('\t')

        if not lines:
            continue

        if len(lines) == 1:  # solely for testing, so that we don't have to use official format
            question = Question("", lines[0].strip())
        else:
            question = Question(lines[0], lines[1].strip())

        if not question.is_valid():
            continue

        syntax_parser.parse(question)

        # print("Trying standard strategy next")
        if standardStrategy(question.syntax, question.syntax_root):
            continue

        # no answer found
        writeAndPrintAnswers(["I don't know"])  # Default answer
