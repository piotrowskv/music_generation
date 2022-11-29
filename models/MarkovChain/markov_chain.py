import random
import os
import numpy as np

DATA_PATH = 'data/sequences'
class Markov_Chain():

    
    def __init__(self):
        self.data = []
        self.tokens = set()
        self.n_grams = set()
        self.tokens_list = []
        self.n_grams_list=[]
        self.probabilities = []
        self.n_grams_next_token = []

    def load_data(self):
        print("Data loading...")
        data_lines = []
        for filename in os.listdir(DATA_PATH):
            data_lines.append(np.load(os.path.join(DATA_PATH, filename)))


        for i in range(len(data_lines)):
            for j in range(data_lines[i].shape[0]):
                self.data.append(data_lines[i][j].tolist())

        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                notes = []
                for k in range(128):
                    if(self.data[i][j][k]==True):
                        notes.append(k)

                self.data[i][j]=tuple(notes)
                self.tokens.add(tuple(notes))
        
        print("Data loaded!")

   
    def generate_n_grams(self, n):
        print("Generating " + str(n) + "-grams")
        for i in range(len(self.data)):
            for j in range(len(self.data[i])-n):
                self.n_grams.add(tuple(self.data[i][j:j+n]))

        self.tokens_list = list(self.tokens)
        self.n_grams_list = list(self.n_grams)
        print(str(n) + "-grams generated!")

    def count_probabilities(self):
        print("Counting probabilities")

        n = len(self.n_grams_list[0])
        n_gram_next = np.ndarray((len(self.n_grams_list,)), dtype=object)
        for i in range(n_gram_next.shape[0]):
            n_gram_next[i]=[]

        for i in range(len(self.data)):
            print(str(i) + "/" + str(len(self.data)))
            for j in range(len(self.data[i])-n-1):
                curr_n_gram =tuple(self.data[i][j:j+n])
                next_note = self.data[i][j+n+1]
                n_gram_next[self.n_grams_list.index(curr_n_gram)].append(next_note)
            
        self.probabilities = np.ndarray((len(self.n_grams_list,)), dtype=object)
        for i in range(n_gram_next.shape[0]):
            self.probabilities[i]={}

        for i in range(len(n_gram_next)):
            for j in range(len(n_gram_next[i])):
                if(len(n_gram_next[i])<=1):
                   self.probabilities[n_gram_next[i]][j]=1
                else: 
                    if(self.probabilities[i].get(n_gram_next[i][j]) is None):
                        self.probabilities[i][n_gram_next[i][j]] = float(n_gram_next[i].count(n_gram_next[i][j]) / len(n_gram_next[i]))
            
        print("Counting probabilities done!")

    def predict(self, initial_notes, length, deterministic, rand, save_path, save_name): 
        prediction = []
        previous_n_gram = initial_notes
        for i in range(len(initial_notes)):
            prediction.append(initial_notes[i])
        for i in range(length):
            idx = None
            if(previous_n_gram in self.n_grams):
                idx = self.n_grams_list.index(previous_n_gram)
            else:
                idx = random.randrange(len(self.probabilities))
            probs = self.probabilities[idx]
            while(len(probs)==0):
                idx = random.randrange(len(self.probabilities))
                probs = self.probabilities[idx]

            next_note = None
            if(random.randrange(100) < rand*100):
                next_note = random.choice(self.tokens_list)
            elif(deterministic):
                next_note = max(probs, key=probs.get)
            else:
                next_note = random.choices(list(probs.keys()), weights=probs.values(), k=1)[0]
            previous_n_gram = previous_n_gram[1:] + (next_note,)
            prediction.append(next_note)

        print(prediction)
        result = np.full((len(prediction), 128), False)
        for i in range(len(prediction)):
            for j in range(len(prediction[i])):
                note = prediction[i][j]
                result[i][note]=True

        os.makedirs(save_path, exist_ok=True)
        np.save('{}/{}'.format(save_path, save_name), result)

                


# 21379, 21133, 21095, 20987, 20750

def driver():
    print("--------------------------------MODEL 1--------------------------------------")
    # 2-grams
    m = Markov_Chain()
    m.load_data()
    m.generate_n_grams(2)
    m.count_probabilities()

    m.predict(m.n_grams_list[20750], 160, True, 0, 'results', 'Test1')
    m.predict(m.n_grams_list[random.randrange(2892)], 120, True, 0.1, 'results', 'Test2')
    m.predict(m.n_grams_list[405], 200, True, 0.25, 'results', 'Test3')
    m.predict(m.n_grams_list[2000], 2000, False, 0, 'results', 'Test4')
    m.predict(m.n_grams_list[94], 2000, False, 0.1, 'results', 'Test5')
    m.predict(m.n_grams_list[2929], 2000, False, 0.15, 'results', 'Test6')
    m.predict(m.n_grams_list[21133], 2000, False, 0.20, 'results', 'Test7')
    m.predict(m.n_grams_list[20987], 2000, False, 0.20, 'results', 'Test8')
    m.predict(m.n_grams_list[4], 2000, False, 0.20, 'results', 'Test9')
    m.predict(m.n_grams_list[1121], 2000, False, 0.25, 'results', 'Test10')

    print("--------------------------------MODEL 2--------------------------------------")


    m3 = Markov_Chain()
    m3.load_data()
    m3.generate_n_grams(3)
    m3.count_probabilities()

    m3.predict(m.n_grams_list[20750], 160, True, 0, 'results', 'Test11')
    m3.predict(m.n_grams_list[random.randrange(500)], 200, True, 0.1, 'results', 'Test12')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, True, 0.25, 'results', 'Test13')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0, 'results', 'Test14')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.05, 'results', 'Test15')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.1, 'results', 'Test16')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.2, 'results', 'Test17')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.2, 'results', 'Test18')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.2, 'results', 'Test19')
    m3.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.25, 'results', 'Test20')

    print("--------------------------------MODEL 3--------------------------------------")

    m4 = Markov_Chain()
    m4.load_data()
    m4.generate_n_grams(4)
    m4.count_probabilities()

    m4.predict(m.n_grams_list[20750], 160, True, 0, 'results', 'Test21')
    m4.predict(m.n_grams_list[random.randrange(500)], 200, True, 0.1, 'results', 'Test22')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, True, 0.25, 'results', 'Test23')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0, 'results', 'Test24')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.05, 'results', 'Test25')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.1, 'results', 'Test26')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.2, 'results', 'Test27')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.2, 'results', 'Test28')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.2, 'results', 'Test29')
    m4.predict(m.n_grams_list[random.randrange(500)], 2000, False, 0.25, 'results', 'Test30')
