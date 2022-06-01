import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

class DistanceBasedModel:
    
    def __init__(self, model, params, distance_func, gamma=0.9):
        self.model = model
        self.params = params
        self.distance_func = distance_func
        self.score_min = -100
        self.score_max = 100
        self.gamma = gamma
        self.df_game = pd.DataFrame(columns = ["word", "score_cemantix", "score_inversed"])
        self.turn = 0
        self.next_word_nb_calls = -1
        self.list_closest_words = self.find_list_centroids()
        #print(self.list_closest_words)
        
            
    def find_list_centroids(self, len_list=100):
        norms = euclidean_distances(np.zeros(self.model.vector_size).reshape(1,self.model.vector_size),
                                    self.model.vectors)
        return [self.model.index_to_key[norms.argsort().argsort()[0][i]] for i in range(len_list)]
    
    
    def find_list_next_words(self, len_list=100):
        word_sorted = self.df_game[["word", "score_inversed"]].sort_values(by="score_inversed")["word"].values
        word_distances = self.distance_func(np.array([self.model.get_vector(w) for w in word_sorted]),
                                           self.model.vectors)

        discount = np.array([self.gamma**i for i in range(len(self.df_game))])

        index_closest_words = np.argpartition(np.matmul(abs(word_distances 
                                                            - self.df_game["score_inversed"].sort_values().values.reshape(-1,1)).T,
                                                        discount),
                                              kth=np.arange(0, 100))
        
        best_words = [self.model.index_to_key[idx] for idx in index_closest_words.reshape(-1)[:len_list]]
        
        
        
        #best_distances = self.distance_func(np.array([self.model.get_vector(w) for w in word_sorted]),
        # ([self.model.get_vector(w) for w in best_words]))
        
        #print(abs(best_distances - self.df_game["score_inversed"].sort_values().values.reshape(-1,1)).T[:10])

        #print(np.matmul(abs(best_distances - self.df_game["score_inversed"].sort_values().values.reshape(-1,1)).T,
        #                                                discount)[:10])

        return best_words
        
        
    def inverse_scaling(self, score_scaled):
        score_std = (self.params["mmScaler"]["min"] 
                     + (-score_scaled - self.score_min) * (self.params["mmScaler"]["max"] 
                                                           - self.params["mmScaler"]["min"]) 
                     / (self.score_max - self.score_min))
        score = (score_std * self.params["stdScaler"]["scale"]) + self.params["stdScaler"]["mean"]
        return score
        
        
    def next_word(self, game):
        if len(game) > self.turn:
            self.df_game.loc[len(self.df_game), "word"] = game.loc[len(game)-1, "word"]
            self.df_game.loc[len(self.df_game)-1, "score_cemantix"] = game.loc[len(game)-1, "score_cemantix"]
            self.df_game.loc[len(self.df_game)-1, "score_inversed"] = self.inverse_scaling(game.loc[len(game)-1, "score_cemantix"])
            self.turn += 1
            self.next_word_nb_calls = -1
            self.list_closest_words = self.find_list_next_words()
            #print(self.list_closest_words[:10])
            
        self.next_word_nb_calls += 1
        return self.list_closest_words[self.next_word_nb_calls]