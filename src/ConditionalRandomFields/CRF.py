import pandas as pd
import numpy as np
import logging
import json
import sys
from src.ConditionalRandomFields.CRFFunctions import Augment, Process, FeatureFunctions, Score, BackProp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Prepare: #MARK: Prepare
    def __init__(self, filename="data/TIM.csv"):
        self.filename = filename
        self.augmenter = Augment() 

        try:
            self.augmenter.split_events()
            self.augmenter.concat_predicates()
            self.augmenter.store_sequences()
            self.augmenter.save_data()
            logger.info(f"Data augmentation completed and saved to {self.augmenter.events_path}")
        except Exception as e:
            logger.error(f"Error during data augmentation: {e}")
            raise

class Train: #MARK: Training
    def __init__(self, weights=None, training_size=0.8, testing_size=0.2, filename="data/aug_TIM.csv", num_features=11):  
        self.data = pd.read_csv(filename)
        self.data = pd.DataFrame(self.data)
        self.training_data = self.data.sample(frac=training_size).reset_index(drop=True) 
        self.validation_data = self.data.sample(frac=testing_size).reset_index(drop=True)
        print(f"📏 Training data size: {len(self.training_data)}, 📏 Validation data size: {len(self.validation_data)}")
        if weights is None:
            self.weights = np.random.rand(num_features)
            self.weights = [weight * (1 - 0.1) - 0.1 for weight in self.weights] 
        else:
            self.weights = weights

        self.avg_loss = 0.0         
        self.validation_avg_loss = 0.0 

    def train(self): #MARK: Train
        if self.training_data is not None:
            total_rows = len(self.training_data)

            count = 0
            sum_loss = 0.0
            for idx, (index, row) in enumerate(self.training_data.iterrows()):
                count += 1
                text = row["full_text"]
                label = row["sequence"].split(" ")
                
                try:
                    processor = Process(label, len(label), text)
                    sequences = processor.get_sequences()
                    tags = processor.get_tags()

                    if len(label) != len(tags):
                        print()  
                        logger.error(f"Length mismatch at row {idx}: {len(label)} labels for {len(tags)} tags")
                        return None
                    
                except Exception as e:
                    print() 
                    logger.error(f"Error processing row {idx}: {e}")
                    continue

                scorer = Score(sequences, label, self.weights, text) 
                feature_functions = FeatureFunctions(tags, label, self.weights, text)
                apply_drop = np.random.choice([True, False])
                true_scores = feature_functions.call_features(apply_drop=apply_drop, is_training=True)
                sum_scores = np.sum(true_scores) if true_scores is not None else 0.0
                z_out = scorer.z_out(tags)
                
                try:
                    backprop = BackProp(self.weights, tags, sequences, text)  
                    true_probability = scorer.probability(true_scores, scorer.z)  
                    loss = backprop.loss(true_probability)
                    self.gradients = backprop.gradient(true_scores, scorer)
                    self.weights = backprop.update_weights(self.gradients)

                    sum_loss += loss
                    self.avg_loss = sum_loss / count if count > 0 else 0.0
                    if true_probability > 1:
                        print(f"\n❌ Probability exceeded 1 at row {idx}: {true_probability:.6f}")
                        
                    print(f"\r🔄 Row {idx + 1}/{total_rows} | 📉 Avg. Loss: {self.avg_loss:.4f} | 💯 True Score: {sum_scores:.4} | ✅ Prob: {true_probability:.6f} | ⚖️ Z: {z_out:.4f} | 🏃 Avg. Gradient: {np.mean(self.gradients):.4f}", 
                          end="", flush=True)
                    
                except Exception as e:
                    print()  
                    logger.error(f"Error in backpropagation for row {idx}: {e}")
                    continue
            
            print(f"\n✅ Training completed! Processed {total_rows} rows.")
            
        return self.weights

    def validation(self): #MARK: Validate
        count = 0
        sum_loss = 0.0
        for idx, (index ,row) in enumerate(self.validation_data.iterrows()):
            text = row["full_text"]
            label = row["sequence"].split(" ")
            
            try:
                processor = Process(label, len(label), text)
                sequences = processor.get_sequences()
                tags = processor.get_tags()

                if len(label) != len(tags):
                    logger.error(f"Length mismatch at validation row {idx}: {len(label)} labels for {len(tags)} tags")
                    continue
                
            except Exception as e:
                logger.error(f"Error processing validation row {idx}: {e}")
                continue

            scorer = Score(sequences, label, self.weights, text) 
            feature_functions = FeatureFunctions(tags, label, self.weights, text)
            true_scores = feature_functions.call_features(is_training=False)
            sum_scores = np.sum(true_scores) if true_scores is not None else 0.0
            z_out = scorer.z_out(tags)
            true_probability = scorer.probability(true_scores, scorer.z)
            backprop = BackProp(self.weights, tags, sequences, text)
            loss = backprop.loss(true_probability)

            sum_loss += loss
            count += 1
            self.validation_avg_loss = sum_loss / count if count > 0 else 0.0
            print(f"\r 🔄 Validation Row {idx + 1}/{len(self.validation_data)} | 📉 Avg. Loss: {self.validation_avg_loss:.4f} | 💯 True Score: {sum_scores:.4f}| ✅ Prob: {true_probability:.6f} | ⚖️ Z: {z_out:.4f}", end="", flush=True)

    def save_weights(self, filename="data/weights.json"):
        try:
            with open(filename, "w") as f:
                json.dump({"weights": {str(i): weight for i, weight in enumerate(self.weights)}}, f)
            logger.info(f"Weights saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving weights to {filename}: {e}")
            raise
    
class Predict: #MARK: Predict
    def __init__(self, input, filename="data/weights.json"):
        try:
            with open(filename, "r") as f:
                self.weights = json.load(f)

            if self.weights:
                self.weights = [float(weight) for weight in self.weights["weights"].values()]

            logger.info(f"Loaded weights from {filename}: {self.weights}")
        except FileNotFoundError:
            logger.warning(f"File {filename} not found, using default weights")
            return None
        
        self.input = input
    
    def predict(self):
        try:
            processor = Process(["T", "TM", "D", "O"], len(self.input.split(" ")), self.input)
            sequences = processor.get_sequences(max_permutations=10000)
            tags = processor.get_tags()
            
            scorer = Score(sequences, self.input.split(" "), self.weights, self.input) 
            scores = scorer.score_sequences(tags)
            if scores:
                best_score = max(scores)
                if sequences:
                    best_sequence = sequences[scores.index(best_score)]
                else:
                    logger.error("No sequences found, cannot determine best sequence")
                    return None

                scorer.z_out(tags)
                logger.info(f"Best sequence found: {best_sequence} with probability {scorer.probability(scores)} and best score {best_score}")
                return best_sequence
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return None
        
    def process_labels(self, labels):
        try:
            task = []
            time = []
            date = []
            filler = []
            for word, label in zip(self.input.split(" "), labels):
                if label == "T":
                    task.append(word)
                elif label == "TM":
                    time.append(word)
                elif label == "D":
                    date.append(word)
                elif label == "O":
                    filler.append(word)
            task = " ".join(task)
            time = " ".join(time)
            date = " ".join(date)
            filler = " ".join(filler)
            return {
                "task": task.strip(),
                "time": time.strip(),
                "date": date.strip(),
                "filler": filler.strip()
            }
        except Exception as e:
            logger.error(f"Error processing labels: {e}")
            return None