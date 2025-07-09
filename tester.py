from src.ConditionalRandomFields.CRF import Predict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_prediction():
    text = input("Enter a event schedule:")
    predicter = Predict(text)
    labels = predicter.predict()
    if labels:
        processed_labels = predicter.process_labels(labels)
        logger.info(f"🔍 Processed labels: {processed_labels}")


if __name__ == "__main__":
    test_prediction()
    print("🔍 Prediction test completed. Check logs for details.")