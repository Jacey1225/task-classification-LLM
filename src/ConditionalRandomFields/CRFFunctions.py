import pandas as pd
import numpy as np
import spacy
import itertools

nlp = spacy.load("en_core_web_md")

class Augment: #MARK: Augmentation
    def __init__(self, data):
        self.data = pd.DataFrame(data)

    def process_labels(self):
        self.data["task"] = self.data["task"].apply(lambda x: x.split(" "))
        self.data["task"] = self.data["task"].apply(lambda x: [label.replace(label, "T") for label in x])

        self.data["time"] = self.data["time"].apply(lambda x: x.replace(x, "TM"))

        self.data["date"] = self.data["date"].apply(lambda x: x.split(" "))
        self.data["date"] = self.data["date"].apply(lambda x: [label.replace(label, "D") for label in x])

    def fillers(self, num_data=1000):
        random_fillers = ["um", "like", "basically", "you know", "I guess", "I think", "so", "let's see"]
        additionals = []
        for i in range(num_data):
            filler = np.random.choice(random_fillers)
            input = np.random.choice(self.data)
            text = input["text"]
            random_index = np.random.choice(0, len(text))
            input["text"] = text[random_index:] + " " + filler + " " + text[:random_index]
            additionals.append(input)
        self.data = pd.concat([self.data, pd.DataFrame(additionals)], ignore_index=True)

    def random_time(self): # -> additional_tasks
        random_time = np.random.randint(0, 12)
        random_minutes = np.random.randint(0, 60)
        random_am_pm = np.random.choice(["AM", "PM"])
        return f"{random_time}:{random_minutes:02d} {random_am_pm}"
    
    def random_date(self): # -> additional_tasks
        random_day = np.random.randint(1, 29)
        random_month = np.random.choice(["January", "February", "March", "April", "May", "June", 
                                         "July", "August", "September", "October", "November", "December"])
        return f"{random_month} {random_day}"

    def additional_tasks(self, num_data=2000):
        orders = ["remind me to", "please input", "I need to", "put", "I have to", "I want to", "make sure that I", 
                  "can you have me"]
        tasks = [
            "clean the house", "buy groceries", "finish data augmentation", "go to the gym",
            "read up on the algorithms book", "work on calculus homework", "work", "wedding", "church service",
            "go to DT", "read bible", "morning prayer", "hangout with friends", "dinner with Dad", "lunch with mom",
            "research new data algorithms", "prepare for presentation", "write essay for english", "free time", 
            "bing watch series", "clean the kitchen", "wash teh car", "buy tickets for the concert", "biuld the CRF model",
            "organize my room", "PBL meeting", "United Hacks hackathon", "print new tools for mom"]
        
        additionals = []
        for i in range(num_data):
            order = np.random.choice(orders)
            task = np.random.choice(tasks)
            time = self.random_time()
            date = self.random_date()
            text = f"{order} {task} at {time} on {date}"
            input = {"text": text, "task": task, "time": time, "date": date}
            additionals.append(input)
        
        return pd.DataFrame(additionals)

class Process: #MARK: Processing 
    def __init__(self, raw_labels, labels, label_length, feature_text): 
        self.nlp = nlp
        self.raw_labels = raw_labels
        self.labels = labels
        self.label_length = label_length
        self.feature_text = feature_text
    
    def get_sequences(self):
        sequences = list(itertools.product(self.labels, repeat=self.label_length))
        return sequences
    
    def split_true(self):
        true_sequence = []
        self.raw_labels = [label.split(" ") for label in self.raw_labels]
        for i, label in enumerate(self.raw_labels):
            label.split(" ")
            if i == 0:
                true_sequence.append(("T", label))
            elif i == 1:
                true_sequence.append(("TM", label))
            elif i == 2:
                true_sequence.append(("D", label))
        return true_sequence
    
    def true_sequence(self):
        true_split = self.split_true()
        label_sequence = []
        for word in self.feature_text.split(" "):
            found = False
            for label, raw_label in true_split:
                if word in raw_label:
                    label_sequence.append(label)
                    found = True
                    break
                else:
                    continue
            if not found:
                label_sequence.append("O")
        return label_sequence
        
    def get_tags(self):
        doc = nlp(self.feature_text)
        tags = [token.tag_ for token in doc]
        return tags


class FeatureFunctions: #MARK: Functions
    def __init__(self, tags, sequence, weights):
        self.tags = tags # POS tags
        self.sequence = sequence # Sequence of labels T for task, D for time or date, or O for irrelevant
        self.weights = weights

    def f1(self, tag, label, i): #Task
        if tag == "VERB" and label == "T":
            if (self.tags[i+1] == "DET" or self.tags[i+1 == "NOUN"]) and i < len(self.tags) - 1:
                return 1
        return 0
    def f2(self, tag, label, i): #Date
        if tag == "NOUN" and label == "D" and self.tags[i-1] == "ADP" and i > 0:
            return 1
        return 0
    
    def f3(self, tag, label, i): #Date
        if tag == "PROPN" and self.tags[i-1] == "ADP" and i > 0:
            if (self.tags[i+1] == "NOUN" or self.tags[i+1] == "NUM") and label == "D" and i < len(self.tags) - 1:
                return 1
        return 0

    def f4(self, tag, label, i): #Task
        if tag == "PART" and label == "O":
            if (self.tags[i+1]== "VERB" and label == "T") and i < len(self.tags) - 1:
                return 1
        return 0
    
    def f5(self, tag, label, i): #Task
        if (tag == "VERB" or tag == "NOUN") and label == "T":
            if (self.tags[i+1] == "ADP" or self.tags[i+1] == "NOUN") and self.sequence[i+1] == "T" and i < len(self.tags) - 1:
                return 1
        return 0
    
    def f6(self, tag, label, i): #Task
        if tag == "ADP" and label == "T":
            if self.tags[i+1] == "PROPN" or self.tags[i+1] == "NOUN" and i < len(self.tags) - 1:
                if self.sequence[i+1] == "T":
                    return 1
        return 0
    
    #TODO: Change for more feature functions
    def call_features(self):
        for i, (tag, label) in enumerate(zip(self.tags, self.sequence)):
            output1 = self.f1(tag, label, i) * self.weights[0]
            output2 = self.f2(tag, label, i) * self.weights[1]
            output3 = self.f3(tag, label, i) * self.weights[2]
            output4 = self.f4(tag, label, i) * self.weights[3]
            output5 = self.f5(tag, label, i) * self.weights[4]
            output6 = self.f6(tag, label, i) * self.weights[5]

        return [output1, output2, output3, output4, output5, output6]
        
class Score: #MARK: Scoring
    def __init__(self, possible_labels, true_label, weights): 
        self.possible_labels = possible_labels
        self.true_label = true_label
        self.weights = weights
        self.z = None
    
    
    def z_out(self, true_score, sequences, tags):
        total = 0
        
        for seq in sequences:
            scorer = FeatureFunctions(tags, seq, self.weights)
            outputs = scorer.call_features()
            for i, output in enumerate(outputs):
                weighted_sum = np.exp(output * self.weights[i])
                total += weighted_sum

        self.z = np.exp(true_score) / total
        return self.z
    
    def single_probability(self, sequence, tags, weights):
        scorer = FeatureFunctions(tags, sequence, self.weights)
        outputs = scorer.call_features()
        weighted_sum = 0
        for i, output in enumerate(outputs):
            weighted_sum += np.exp(output * weights[i])
        
        return weighted_sum / self.z if self.z is not None else 0
    
class BackProp: #MARK: Backpropagation
    def __init__(self, weights, tags, sequences, z_out, learning_rate=0.01):
        self.weights = weights
        self.tags = tags
        self.sequences = sequences
        self.learning_rate = learning_rate
        
        self.z_out = z_out

    def loss(self, true_probability):
        loss = -np.log(true_probability)
        return loss

    def gradient(self, true_score):
        gradients = []
        for seq in self.sequences:
            self.scorer = FeatureFunctions(self.tags, seq, self.weights)
            outputs = self.scorer.call_features()
            for i, output in enumerate(outputs):
                gradient = (output * self.z_out) - true_score
                gradients.append(gradient)

        return gradients
    
    def update_weights(self, gradients):
        for i in range(len(self.weights)):
            self.weights[i] -= self.learning_rate * gradients[i]

        return self.weights