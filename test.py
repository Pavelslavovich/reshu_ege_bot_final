import pandas as pd
import os

tasks_list = [9, 10, 11, 12, 13, 15, 16, 17, 18, 19]

os.chdir('tasks')

for task in tasks_list:
    if os.path.exists(f'task{task}') == False:
        os.mkdir(f'task{task}')
        os.chdir(f'task{task}')
    else:
        os.chdir(f'task{task}')
    tasks_df = pd.DataFrame({'task' : [], 'solution' : [], 'answer' : []})
    leaderboard_df = pd.DataFrame({'username' : [], 'full_name' : [], 'count_correct' : [], 'count_false' : [], 'points' : []})
    tasks_df.to_csv(f'task{task}.csv', index=None)
    leaderboard_df.to_csv(f'leaderboard{task}.csv', index=None)
    open(f'task{task}_urls.txt', 'w', encoding='utf-8')
    os.chdir('..')