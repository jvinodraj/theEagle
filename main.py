from src.data_loader import DataLoader

def main():
    fit_file_path = 'data/raw/15-Feb-2025.fit'
    output_path = 'data/processed/cleaned_fit_data.csv'

    loader = DataLoader(fit_file_path)
    loader.read_fit_file()
    loader.preprocess_data()
    loader.save_clean_data(output_path)

if __name__ == '__main__':
    main()
