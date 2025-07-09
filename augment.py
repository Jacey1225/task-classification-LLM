from src.ConditionalRandomFields.CRFFunctions import Augment

def PrepareData():
    augmenter = Augment()
    augmenter.split_events()
    augmenter.concat_predicates()
    augmenter.store_sequences()
    augmenter.save_data()

if __name__ == "__main__":
    print("🚀 Starting data preparation...")
    PrepareData()
    print("✅ Data preparation complete!")