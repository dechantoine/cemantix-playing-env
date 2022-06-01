import pandas as pd
import json

import requests


def get_score_cemantix(word, session):
    response = session.post("https://cemantix.herokuapp.com/score", data={"word" : word}).json()
    if not "error" in list(response.keys()):
        return response["score"]*100
    else :
        return False
    

    
def play_cemantix(strategy, resume=None, max_turn=100):
    session = requests.Session()
    
    if resume is None:
        df_game = pd.DataFrame(columns = ["word", "score_cemantix"])
        turn = 0
        score_max = -100
    else:
        df_game = resume
        turn = len(df_game)
        score_max = df_game["score_cemantix"].max()
    
    while (turn < max_turn) and (score_max < 100):
        score_cemantix = False
        k = 0
        
        while not score_cemantix:
            word = strategy.next_word(df_game)
            if word not in df_game["word"].values:
                score_cemantix = get_score_cemantix(word, session)
            k += 1
        
        df_game.loc[len(df_game)] = [word, score_cemantix]
        score_max = df_game["score_cemantix"].max()
        turn += 1
        
        
    return df_game