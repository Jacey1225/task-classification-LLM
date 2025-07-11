import unittest
import logging
import time
import threading
import os

os.chdir("/Users/jaceysimpson/Vscode/task-classification-LLM")
from src.ConditionalRandomFields.CRF import Train

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestTrainClass(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stopwatch_running = False
        self.epoch_start_time = None
        self.total_start_time = None
        
    def real_time_stopwatch(self, epoch_num):
        """Real-time stopwatch that updates every second"""
        seconds = 0
        while self.stopwatch_running:
            time.sleep(1)
            if self.stopwatch_running: 
                seconds += 1
                elapsed_total = time.time() - self.total_start_time
                logger.info(f"⏱️  Epoch {epoch_num} - {seconds}s elapsed | Total: {elapsed_total:.0f}s")

    def test_train_runs(self, epochs=10):
        try:
            weights = None
            self.total_start_time = time.time()
            
            for i in range(epochs):
                epoch_num = i + 1
                logger.info(f"🚀 Starting training epoch {epoch_num}/{epochs}")
                
                self.epoch_start_time = time.time()
                self.stopwatch_running = True
                
                stopwatch_thread = threading.Thread(target=self.real_time_stopwatch, args=(epoch_num,))
                stopwatch_thread.daemon = True
                stopwatch_thread.start()
                
                trainer = Train(weights=weights, num_features=9)
                weights = trainer.train()
                
                self.stopwatch_running = False
                
                epoch_end_time = time.time()
                epoch_duration = epoch_end_time - self.epoch_start_time
                total_elapsed = epoch_end_time - self.total_start_time
                
                logger.info(f"✅ Completed epoch {epoch_num}/{epochs}")
                logger.info(f"📊 Epoch {epoch_num} final time: {epoch_duration:.2f}s | Total elapsed: {total_elapsed:.2f}s")
                logger.info(f"⚖️  Updated weights: {[f'{w:.4f}' for w in weights]}")
                logger.info(f"{'='*60}")
                
            total_duration = time.time() - self.total_start_time
            avg_epoch_time = total_duration / epochs
            
            logger.info(f"🏁 TRAINING COMPLETE!")
            logger.info(f"📈 Total training time: {total_duration:.2f} seconds")
            logger.info(f"⏱️  Average time per epoch: {avg_epoch_time:.2f} seconds")
            logger.info(f"🔢 Total epochs completed: {epochs}")
            logger.info(f"{'='*60}")
            
            self.assertTrue(True)
        except Exception as e:
            self.stopwatch_running = False  
            self.fail(f"Training failed with exception: {e}")

if __name__ == "__main__":
    unittest.main()
