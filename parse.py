# html parser with BeautifulSoup
from bs4 import BeautifulSoup
import time
import pandas as pd

def parse_html_document(path_to_document):
    html_document = open(path_to_document, 'r', encoding='utf-8')
    html_document_in_str = ""
    for line in html_document:
        html_document_in_str += line
    soup = BeautifulSoup(html_document_in_str, 'html.parser')

    notParseProblems = soup.find_all("div", class_="problem_container")

    tasks = []
    solutions = []
    answers = []

    for curTask in notParseProblems:
        parseTasks = curTask.find('div', class_='nobreak').find('div', class_='pbody').find_all('p')
        parseTask = '_' + parseTasks[0].get_text().strip() + '_'

        for i in range(1, len(parseTasks)):
            parseTask += parseTasks[i].get_text().strip()
            parseTask += '\n'
        tasks.append(parseTask)

    for curSolution in notParseProblems:
        parseSolutions = curSolution.find('div', class_='solution').find_all('p')
        parseSolution = ''
        for i in parseSolutions:
            parseSolution += i.get_text().strip()
        solutions.append(parseSolution)
    
    for curAnswer in notParseProblems:
        parseAnswer = curAnswer.find('div', class_='answer')
        answers.append(parseAnswer.get_text()[7:])

    print(len(answers), len(solutions), len(tasks))

    df = pd.DataFrame({'task' : tasks, 'solution' : solutions, 'answer' : answers})
    
    return df

