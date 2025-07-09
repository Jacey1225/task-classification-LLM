from src.ConditionalRandomFields.CRF import Train
import numpy as np
import logging
import sys
import threading
import time
import select
import tty
import termios


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def TrainModel(epochs=50, num_features=11):
    
    try: 
        weights = np.random.rand(num_features)
        weights = [weight * (1 - 0.1) - 0.1 for weight in weights]  
        print(f"Initial weights({len(weights)}): {weights}")
        
        for epoch in range(epochs):
            print(f"\r🏋️‍♂️ Epoch {epoch + 1}/{epochs} - Starting training...", end="", flush=True)
            
            trainer = Train(weights=weights)
            trainer.train()
            weights = trainer.weights
            
            print(f"\r🏁 Epoch {epoch + 1}/{epochs} completed! Current weights: {weights}    ", 
                  end="", flush=True)
            
            time.sleep(0.5)
            
            trainer.validation()
            if abs(trainer.validation_avg_loss - trainer.avg_loss) > 0.75:
                print(f"\n⚠️ Validation loss drifted significantly: {trainer.validation_avg_loss:.4f} vs {trainer.avg_loss:.4f}. Early stopping...", end="", flush=True)
                break
        
        print()  
        trainer.save_weights()
        
    except KeyboardInterrupt:
        print(f"\n🔥 Training interrupted by Ctrl+C --> Current Weights: {weights}")
    except Exception as e:
        print(f"\n❌ Training failed with error: {e}")

if __name__ == "__main__":
    TrainModel()
    print("✅ Model training completed successfully!")