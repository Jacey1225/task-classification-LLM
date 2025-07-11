import random
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 🧪 ✅ ❌
class FeatureFunctions:
    def __init__(self, tags, sequence, weights, feature_text):
        self.tags = tags
        self.sequence = sequence
        self.weights = weights
        self.raw_text = feature_text
        self.feature_text = feature_text.split(" ")
        self.previous_weights = None

    def f1(self, tag, label, i): # TIME ✅
        if label == "TM":
            if "NUM" == tag or "NOUN" == tag:
                if ":" in self.raw_text or "AM" in self.raw_text.upper() or "PM" in self.raw_text.upper():
                    return 1
        return 0
    
    def f2(self, tag, label, i): # DATE ✅
        if label == "D":
            if any(month in self.feature_text for month in ["today", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]):
                return 1
        return 0
    
    def f3(self, tag, label, i): # DATE ✅
        if i > 0 and i < len(self.tags) - 1:
            if tag == "PROPN" and self.tags[i+1] == "NOUN":
                if label == "D" and i+1 < len(self.sequence) and self.sequence[i+1] == "D":
                    return 1
        return 0
    
    def f5(self, tag, label, i): # TASK ✅ 
        if i > 0 and i < len(self.tags) - 1:
            if tag == "NOUN" and (self.tags[i-1] == "PROPN" or self.tags[i+1] == "NOUN"):
                if label == "T" and ((i-1 >= 0 and self.sequence[i-1] == "T") or (i+1 < len(self.sequence) and self.sequence[i+1] == "T")):
                    return 1
        return 0
    
    def f7(self, tag, label, i): #TASK ✅
        if i > 0 and i < len(self.tags) - 1:
            if tag in ["NOUN", "PROPN", "VERB"] and self.tags[i-1] in ["VERB", "ADP", "ADJ", "ADV", "PRON"]:
                if label == "T":
                    return 2
        return 0

    def f9(self, tag, label, i): #TIME 🧪
        if i >= 2 and i < len(self.tags) - 1:  
            if label == "TM" and self.sequence[i-2] == "TM":
                return 1
        return 0

    def f10(self, tag, label, i): #FILLER ✅
        if i == 0 or (i < len(self.tags) - 1 and i + 1 < len(self.sequence)):  
            if tag in ["ADP", "PRON", "PROPN", "VERB", "NOUN"] and i + 1 < len(self.tags) and self.tags[i+1] in ["ADP", "PRON", "PROPN", "VERB", "NOUN"]:
                if label == "O" and self.sequence[i+1] == "O":
                    return 1.5
        return 0
    
    def f11(self, tag, label, i): #DATE ✅ 
        if i < len(self.feature_text): 
            if self.feature_text[i] in ["today", "tomorrow", "tonight", "now", "next", "morning", "night", "afternoon", "evening", "noon", "midnight"]:
                if label == "D":
                    return 1
        return 0

    def f13(self, tag, label, i): #TASK 🧪
        if i > 0 and i < len(self.tags) - 1:
            if tag in ["NOUN", "PROPN", "VERB"] and self.tags[i-1] == "VERB":
                if label == "T" and self.sequence[i-1] == "T":
                    return 2
        return 0
    
    def f14(self, tag, label, i): #FILLER + TASK 🧪
        if i < len(self.tags) - 2:
            if tag in ["ADP", "PRON", "PROPN", "NOUN"]:
                if label == "O" and self.sequence[i+1] == "O" and self.sequence[i+2] == "T": 
                    return 1.5
        return 0
    
    def dropout(self, drop_rate=0.2):
        if self.weights is None or len(self.weights) == 0:
            logger.warning("No weights available for dropout")
            return self.weights
        
        try:
            active_weights = self.weights.copy()
            
            max_possible_drops = len(self.weights) - 1
            calculated_drops = int(len(self.weights) * drop_rate)
            
            num_weights_to_drop = max(1, min(calculated_drops, max_possible_drops))
            
            if num_weights_to_drop <= 0:
                return active_weights
            
            droppable_indices = [i for i, w in enumerate(self.weights) if w != 0]
            
            if len(droppable_indices) == 0:
                logger.warning("All weights are zero, cannot apply dropout")
                return active_weights
            
            actual_drops = min(num_weights_to_drop, len(droppable_indices))
            
            if actual_drops > 0:
                weights_to_drop = random.sample(droppable_indices, actual_drops)
                
                for idx in weights_to_drop:
                    active_weights[idx] = 0
            
            return active_weights
            
        except Exception as e:
            logger.error(f"Error in dropout function: {e}")
            return self.weights

    def call_features(self, apply_drop=False, is_training=True):
        if len(self.tags) != len(self.sequence):
            logger.error(f"Tags and sequence lengths do not match: {len(self.tags)} vs {len(self.sequence)}")
            return None
        
        if is_training and self.weights is not None and apply_drop:
            active_weights = self.dropout()
        else:
            active_weights = self.weights
            
        if active_weights is None:
            logger.warning("Active weights is None, using original weights")
            active_weights = self.weights
        
        feature_functions = [
            self.f1, self.f2, self.f3,
            self.f5, self.f7, self.f9,
            self.f10, self.f11, self.f13, 
            self.f14]
        
        if len(active_weights) < len(feature_functions):
            logger.error(f"Not enough weights: {len(active_weights)} weights for {len(feature_functions)} features")
            return None
        
        outputs = [0.0] * len(feature_functions)
        
        try:
            for i in range(len(self.tags)):
                if i >= len(self.sequence):  
                    logger.warning(f"Index {i} exceeds sequence length {len(self.sequence)}")
                    break
                    
                tag = self.tags[i]
                label = self.sequence[i]
                
                for j, feature_function in enumerate(feature_functions):
                    if j < len(active_weights):
                        try:
                            feature_value = feature_function(tag, label, i)
                            outputs[j] += feature_value * active_weights[j]
                        except IndexError as e:
                            logger.error(f"Index error in feature {j} at position {i}: {e}")
                            continue
            
            return outputs
            
        except Exception as e:
            logger.error(f"Error in call_features: {e}")
            return None
