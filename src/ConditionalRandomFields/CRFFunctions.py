import pandas as pd
import numpy as np
import spacy
import itertools
import logging
import random
import datetime
import ast
from src.ConditionalRandomFields.FeatureFunctions import FeatureFunctions

nlp = spacy.load("en_core_web_md")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#PYTHONUNBUFFERED=1 python -m unittest -b tests/test_train.py

class Augment: #MARK: Augmentation
    def __init__(self, events_path="data/training-events.csv", predicate_path="data/predicate_phrases.csv"):
        self.events_path = events_path
        self.predicate_path = predicate_path
        self.raw_events = pd.read_csv(events_path)
        self.predicate_data = pd.read_csv(predicate_path)
        logger.info(f"Data loaded from {events_path} and {predicate_path}")

        self.data = pd.DataFrame(columns=["full_text", "event", "start_time", "end_time", "date", "predicate", "sequence"])

    def add_row(self, event, start_time, end_time, date, predicate=None):
        if "-" in event:
            event = event.replace("-", " "   )
        if "'" in event:
            event = event.replace("'", "")
        if "/" in event:
            event = event.replace("/", " ")
        new_row = pd.DataFrame({
            "full_text": [""],
            "event": [event], 
            "start_time": [start_time], 
            "end_time": [end_time],
            "date": [date],
            "predicate": [predicate],
            "sequence": [""]
        })
        self.data = pd.concat([self.data, new_row], ignore_index=True)

    def split_events(self):
        for index, row in self.raw_events.iterrows():
            try:
                info = ast.literal_eval(row["events"])
                for i, item in enumerate(info):
                    if item[3] == "":
                        self.add_row(item[0], item[1], item[2], "today")
                    else:
                        self.add_row(item[0], item[1], item[2], item[3])
            except Exception as e:
                logger.error(f"Error processing events in row {index}: {e}")
                continue

    def concat_predicates(self):
        for index, row in self.data.iterrows():
            event = row["event"]
            random_fix = random.choice(["prefix", "suffix"])
            random_phrase = random.choice(self.predicate_data[random_fix])
            if "-" in random_phrase:
                random_phrase = random_phrase.replace("-", " ")
            if "'" in random_phrase:
                random_phrase = random_phrase.replace("'", "")

            if random_phrase:
                if random_fix == "prefix":
                    self.data.at[index, "predicate"] = random_phrase
                    self.data.at[index, "full_text"] = f"{random_phrase} {event} on {row['date']} from {row['start_time']} to {row['end_time']}"
                else:
                    self.data.at[index, "predicate"] = random_phrase
                    self.data.at[index, "full_text"] = f"{event} {random_phrase} on {row['date']} from {row['start_time']} to {row['end_time']}"

    def store_sequences(self):
        for index, row in self.data.iterrows():
            full_text_tokens = row["full_text"].split(" ")
            sequence = []
            for token in full_text_tokens:
                if token.lower() in str(row["predicate"].lower()):
                    sequence.append("O")
                    continue

                elif token.lower() in str(row["event"].lower()):
                    sequence.append("T")
                    continue

                elif token.lower() in str(row["date"].lower()):
                    sequence.append("D")
                    continue

                elif token.lower() in str(row["start_time"].lower()) or str(token.lower() in row["end_time"].lower()):
                    sequence.append("TM")
                    continue
                else:
                    sequence.append("O")

            if len(sequence) != len(full_text_tokens):
                logger.error(f"Sequence length mismatch at index {index}: {len(sequence)} vs {len(full_text_tokens)}")
                return None
            self.data.at[index, "sequence"] = " ".join(sequence)
    
    def save_data(self, filename="data/aug_TIM.csv"):
        try:
            self.data.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")
            raise
                    
class Process: #MARK: Processing 
    def __init__(self, label, label_length, feature_text): 
        self.nlp = nlp
        self.label = label
        self.label_length = label_length
        self.feature_text = feature_text

    def validate_lengths(self, sequences):
        for seq in sequences:
            if len(seq) != self.label_length:
                logger.error(f"Sequence length mismatch: {len(seq)} vs {self.label_length}")
                return False
        return True

    def get_sequences(self, max_permutations=None):
        if not max_permutations:
            max_permutations = 1000

        sequences_iter = itertools.product(self.label, repeat=self.label_length)
        sequences = list(itertools.islice(sequences_iter, max_permutations))
        random.shuffle(sequences)

        if not self.validate_lengths(sequences):
            logger.error("Validation failed: Sequence lengths do not match the expected label length.")
            return None
        return sequences
        
    def get_tags(self):
        doc = nlp(self.feature_text)
        tags = [token.pos_ for token in doc]
        return tags
class Score: #MARK: Scoring
    def __init__(self, possible_labels, true_label, weights, feature_text): 
        self.possible_labels = possible_labels
        self.true_label = true_label
        self.weights = weights
        self.feature_text = feature_text
        self.z = None

    def score_sequences(self, tags):
        scores = []
        try:
            for seq in self.possible_labels:
                scorer = FeatureFunctions(tags, seq, self.weights, self.feature_text)
                outputs = scorer.call_features(is_training=False)
                if outputs is not None:
                    score = np.sum(outputs)
                    scores.append(score)
            return scores
        except Exception as e:
            logger.error(f"Error scoring sequences: {e}")
            return None
    
    def z_out(self, tags):
        total = 0
        
        try:
            for seq in self.possible_labels:
                scorer = FeatureFunctions(tags, seq, self.weights, self.feature_text)
                outputs = scorer.call_features()
                if outputs is not None:
                    score = np.sum(outputs)
                    total += np.exp(score)
                
        except Exception as e:
            logger.error(f"Error calculating Z value: {e}")
            return None

        self.z = total
        if self.z is None or not np.isfinite(self.z):
            logger.error("Z value is not set or invalid. Returning small default value.")
            self.z = 1e-10

        return self.z
    
    def probability(self, true_scores, z_out=None):
        if self.z is None:
            self.z = z_out
        if self.z is None or not np.isfinite(self.z):
            logger.error("Z value is not set or invalid. Please call z_out() before calculating probability.")
            return 1e-10
        
        try:
            weighted_sum = np.sum(true_scores)
            log_prob = np.exp(weighted_sum) / self.z
            
            return max(log_prob, 1e-10) 
        except Exception as e:
            logger.error(f"Error calculating single probability: {e}")
            return 1e-10
        
class BackProp: #MARK: BackProp
    def __init__(self, weights, tags, sequences, feature_text="", learning_rate=0.008):
        self.weights = weights
        self.tags = tags
        self.sequences = sequences
        self.learning_rate = learning_rate
        self.feature_text = feature_text
        
    def loss(self, true_probability):
        if true_probability is None or true_probability <= 0:
            logger.warning(f"Invalid true_probability: {true_probability}, using small value")
            true_probability = 1e-10
        
        try:
            prob = max(true_probability, 1e-10)
            loss = -np.log(prob)
            
            if not np.isfinite(loss):
                logger.warning(f"Invalid loss calculated: {loss}, using default")
                loss = 10.0
                
            return round(float(loss), 4)
        except Exception as e:
            logger.error(f"Error calculating loss: {e}")
            return 10.0
    
    def gradient(self, true_scores, scorer: Score):
        gradients = []

        expected_f = [0.0] * len(self.weights)  
        for seq in self.sequences:
            feature_functions = FeatureFunctions(self.tags, seq, self.weights, self.feature_text)
            scores = feature_functions.call_features()
            score_probability = scorer.probability(scores)
            
            if scores is not None and score_probability is not None:
                if np.isfinite(score_probability) and score_probability > 0:
                    for i, feature_output in enumerate(scores):
                        if i < len(expected_f) and np.isfinite(feature_output):
                            expected_f[i] += float(feature_output) * float(score_probability)
                else:
                    logger.warning(f"Invalid score_probability: {score_probability}")

        for i in range(len(self.weights)):
            if i < len(true_scores):
                gradient = expected_f[i] - float(true_scores[i])
                gradients.append(gradient)
            else:
                gradients.append(0.0)

        return np.clip(gradients, -1, 1) 
    #MARK: HP
    def normalize_weights(self, l2_strength=0.001): #0.001
        try:
            l2_norm = np.sqrt(sum(w**2 for w in self.weights))
            
            if l2_norm > 0:
                for i in range(len(self.weights)):
                    self.weights[i] = self.weights[i] / (1 + l2_strength * l2_norm)
            
            for i in range(len(self.weights)):
                self.weights[i] = np.clip(self.weights[i], -0.5, 0.5)
            
            return self.weights
        except Exception as e:
            logger.error(f"Error normalizing weights: {e}")
            return self.weights
    
    def update_weights(self, gradients):
        for i in range(len(self.weights)):
            self.weights[i] -= self.learning_rate * gradients[i]

        self.weights = self.normalize_weights()
        return self.weights