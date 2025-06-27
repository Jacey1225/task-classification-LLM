import pandas as pd
import numpy as np
from src.ConditionalRandomFields.CRFFunctions import Augment, Process, FeatureFunctions, Score, BackProp

class Prepare:
    def __init__(self, filename="data/TIM.csv"):
        self.filename = filename
        self.data = pd.read_csv(filename)
        self.augmenter = Augment(self.data) 
        self.new_data = self.augmenter.fillers()
        self.new_data = self.augmenter.additional_tasks()
        self.new_data = self.augmenter.process_labels()

class Train:
    def __init__(self, train_set=0.8, test_set=0.2, num_features=6):
        self.prepare = Prepare()
        self.raw_data = self.prepare.data
        self.data = self.prepare.new_data
        self.weights = np.random.rand(num_features)
        self.weights = [weight * (1 - 0.1) - 0.1 for weight in self.weights] 
        

    def train(self):
        if self.data is not None:
            for index, row in self.data.iterrows():
                text = row["text"]
                labels = row[["task", "time", "date"]].tolist()

                raw_row = self.raw_data[index]
                raw_labels = raw_row[["task", "time", "date"]].tolist()

                processor = Process(raw_labels, labels, len(text.split(" ")), text)
                sequences = processor.get_sequences()
                true_sequence = processor.true_sequence()
                tags = processor.get_tags()

                scorer = Score(sequences, true_sequence, self.weights)
                feature_functions = FeatureFunctions(tags, true_sequence, self.weights)
                true_score = feature_functions.call_features()
                scorer.z_out(true_score, sequences, tags)
                
                backprop = BackProp(self.weights, tags, sequences, scorer.z)
                self.gradients = backprop.gradient(true_score)
                self.weights = backprop.update_weights(self.gradients)
                true_probability = scorer.single_probability(true_sequence, tags, self.weights)
                loss = backprop.loss(true_probability)
                print(f"Loss for row {index}: {loss}")

                




                
    
