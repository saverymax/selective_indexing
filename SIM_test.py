"""
Verify performance of system on test data
"""

from combined_model import *
from daily_update_file_parser import parse_update_file
from preprocess_CNN_data import get_batch_data 
from preprocess_voting_data import preprocess_data

def main(XML_path, journal_ids_path, word_indicies_path):
    """
    Main function to run voting and CNN, combine results,
    adjust decision threshold, and make new predictions
    """
    
    COMBINED_THRESHOLD = .0045
    citations = parse_update_file(XML_path) 
    voting_citations = preprocess_data(citations)
    voting_predictions = run_voting(voting_citations)
    CNN_citations = get_batch_data(citations, journal_ids_path, word_indicies_path)
    cnn_predictions = run_CNN(CNN_citations)
    combined_predictions = combine_predictions(voting_predictions, cnn_predictions)
    adjusted_predictions = adjust_thresholds(combined_predictions, threshold=COMBINED_THRESHOLD)
    print(adjusted_predictions)
    with open("SIM_test_results", "w") as f:
    f.write(classification_report(dfm['y_true'], adjusted_predictions))

if __name__ == "__main__":
    test_path = ".xml"
    #XML_path = "sample_xml.xml"
    journal_ids_path = "journal_ids.txt"
    word_indices_path = "word_indices.txt"
    main(XML_path, journal_ids_path, word_indices_path)
