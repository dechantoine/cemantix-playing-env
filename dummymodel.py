class DummyModel:
    
    def __init__(self, model):
        self.model = model
        self.next_word_nb_calls = -1
        
    def next_word(self, game):
        self.next_word_nb_calls += 1
        return self.model.index_to_key[self.next_word_nb_calls]