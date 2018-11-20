import argparse
from pathlib import Path

from combined_model import *
from daily_update_file_parser import parse_update_file
from preprocess_CNN_data import get_batch_data 
from preprocess_voting_data import preprocess_data
from misindexed_journal_ids import misindexed_ids

def get_args():
    """
    Get command line parser
    """

    parser = argparse.ArgumentParser(description="Arguments for initializing classifier")
    parser.add_argument("--path",
                        dest="path",
                        help="Path to XML containing citations")
    parser.add_argument("--no-group-thresh",
                        dest="group_thresh",
                        action="store_false",
                        help="If included, do not use predetermined threshold for science and jurisprudence groups")
    parser.add_argument("--no-journal-drop",
                        dest="journal_drop",
                        action="store_false",
                        help="If included, model will make predictions for misindexed journals that have been shown to be difficult to classify")

    return parser

def drop_predictions(prediction_dict, adjusted_predictions):
    """
    Convert predictions of citations from 
    misindexed citations to N/A
    """

    for i, journal_id in enumerate(prediction_dict['journal_ids']):
        if journal_id in misindexed_ids:
            adjusted_predictions[i] = "N/A"

    return adjusted_predictions

def save_predictions(adjusted_predictions, prediction_dict, pmids):
    """
    Save predictions to file in format
    pmid|binary prediction|probability
    """
    
    with open("citations_predictions.txt", "w") as f:
        for i, prediction in enumerate(adjusted_predictions):
            f.write("{0}|{1}|{2}\n".format(pmids[i], prediction, prediction_dict['predictions'][i]))

def main(XML_path, journal_ids_path, word_indicies_path, group_thresh, journal_drop):
    """
    Main function to run voting and CNN, combine results,
    adjust decision threshold, and make predictions
    """
    
    citations = parse_update_file(XML_path) 
    voting_citations, journal_ids, pmids = preprocess_data(citations)
    voting_predictions = run_voting(voting_citations)
    CNN_citations = get_batch_data(citations, journal_ids_path, word_indicies_path)
    cnn_predictions = run_CNN(CNN_citations)
    combined_predictions = combine_predictions(voting_predictions, cnn_predictions)
    prediction_dict = {'predictions': combined_predictions, 'journal_ids': journal_ids}
    adjusted_predictions = adjust_thresholds(prediction_dict, group_thresh) 
    # Convert predictions for citations from misindexed journals
    if journal_drop:
        adjusted_predictions = drop_predictions(prediction_dict, adjusted_predictions)
    save_predictions(adjusted_predictions, prediction_dict, pmids)

if __name__ == "__main__":
    args = get_args().parse_args()
    journal_ids_path = "journal_ids.txt"
    word_indices_path = "word_indices.txt"
    main(args.path, journal_ids_path, word_indices_path, args.group_thresh, args.journal_drop)
