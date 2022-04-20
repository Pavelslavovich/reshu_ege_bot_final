import random
import pandas as pd
import ranks
import numpy as np
import os

class Task(object):
    def __init__(self, statement, solution, answer):
        self.statement = statement
        self.solution = solution
        self.answer = answer

user_ids = set()
current_task = dict()
dataframes = dict()
tasks_list = dict()

def init():
    global_tasks_list = []
    os.chdir('tasks')
    for task_number in range(1, 26):
        if os.path.exists(f'task{task_number}') == True:
            dataframes[task_number] = pd.read_csv(f'task{task_number}/leaderboard{task_number}.csv')
            tasks_list[task_number] = pd.read_csv(f'task{task_number}/task{task_number}.csv')
            global_tasks_list.append(task_number)
        else:
            print(f'folder task{task_number} does not exists :(')
    os.chdir('..')
    return global_tasks_list

def change_dataframe(dataframe_number : int):
    dataframes[dataframe_number].to_csv(f'tasks/task{dataframe_number}/leaderboard{dataframe_number}.csv', index=None)

def get_leaderboard(user, task_number : int):
    userid = user.id
    if task_number == 0:
        dataframe = pd.DataFrame({'username' : [], 'full_name' : [], 'count_correct' : [], 'count_false' : [], 'points' : []})
        for task, df in dataframes.items():
            for index, row in df.iterrows():
                current_user_id = row['username']
                current_full_name = row['full_name']
                if len(dataframe.loc[dataframe['username'] == current_user_id]) == 0:
                    dataframe.loc[len(dataframe)] = [current_user_id, current_full_name, int(0), int(0), int(0)]
                dataframe.loc[dataframe['username'] == current_user_id, 'count_correct'] += int(row['count_correct'])
                dataframe.loc[dataframe['username'] == current_user_id, 'count_false'] += int(row['count_false'])
                dataframe.loc[dataframe['username'] == current_user_id, 'points'] += int(row['points'])
    else:
        dataframe = dataframes[task_number]

    sort_list = []
    was_user = 1
    for index, row in dataframe.iterrows():
        sort_list.append([row['points'], row['full_name'], ranks.get_rank(row['points']), row['username']])

    sort_list.sort()
    sort_list.reverse()

    return_leaderboard = ''

    for c in range(0, min(len(sort_list), 7)):
        return_leaderboard += str(c + 1)
        return_leaderboard += ") "
        return_leaderboard += sort_list[c][1]
        return_leaderboard += " | "
        return_leaderboard += str(sort_list[c][0])
        return_leaderboard += " | "
        return_leaderboard += sort_list[c][2]
        return_leaderboard += '\n'
        if sort_list[c][3] == user.id:
            was_user = 0
    
    if return_leaderboard == '':
        return 'Эх, пока что никто не решал данное задание, но вы можете быть первым!'

    if was_user:
        return_leaderboard += '...\n'
        for c in range (len(sort_list)):
            if sort_list[c][3] == user.id:
                return_leaderboard += str(c + 1)
                return_leaderboard += ") "
                return_leaderboard += sort_list[c][1]
                return_leaderboard += " | "
                return_leaderboard += str(sort_list[c][0])
                return_leaderboard += " | "
                return_leaderboard += sort_list[c][2]
                return_leaderboard += '\n'
                break

    return return_leaderboard

def get_task(user, task_number : int):
    print(len(tasks_list[task_number]))
    global current_task
    global user_ids
    userid = user.id
    user_full_name = user.full_name

    if (userid in user_ids) == False:
        user_ids.add(userid)
        current_task[userid] = []

    if len(dataframes[task_number].loc[dataframes[task_number]['username'] == userid]) == 0:
        dataframes[task_number].loc[len(dataframes[task_number])] = [userid, user_full_name, 0, 0, 0]
        change_dataframe(task_number)

    cur_task = ""
    rand_value = random.randint(0, len(tasks_list[task_number]) - 1)
    save_task = Task(tasks_list[task_number]['task'][rand_value], 
        tasks_list[task_number]['solution'][rand_value], 
        tasks_list[task_number]['answer'][rand_value]
    )
    cur_task += save_task.statement

    current_task[userid] = save_task
    return cur_task

def check_task(user, task_number : int, result : str):
    answer = ""
    return_value = ""
    userid = user.id
    user_full_name = user.full_name

    answers = current_task[userid].answer.lower().split('|')

    if result.lower() in answers:
        dataframes[task_number].loc[dataframes[task_number]['username'] == userid, 'count_correct'] += 1
        dataframes[task_number].loc[dataframes[task_number]['username'] == userid, 'points'] += 1
        return_value = "True"
    else:
        get_solution = ""
        dataframes[task_number].loc[dataframes[task_number]['username'] == userid, 'count_false'] += 1
        dataframes[task_number].loc[dataframes[task_number]['username'] == userid, 'points'] -= 1
        get_solution += current_task[userid].solution
        return_value = get_solution

    current_task[userid] = []
    change_dataframe(task_number)

    return return_value
