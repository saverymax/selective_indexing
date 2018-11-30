import argparse
from pkg_resources import resource_string

from .combined_model import *
from .daily_update_file_parser import parse_update_file
from .preprocess_CNN_data import get_batch_data 
from .preprocess_voting_data import preprocess_data
from .misindexed_journal_ids import misindexed_ids
from SIS.SIS_tests.SIS_test import SIS_test_main

def get_args():
    """
    Get command line parser
    """

    parser = argparse.ArgumentParser(description="Arguments for initializing classifier")
    parser.add_argument("--path",
                        dest="path",
                        help="Path to XML containing batch of citations")
    parser.add_argument("--no-group-thresh",
                        dest="group_thresh",
                        action="store_false",
                        help="If included, do not use predetermined threshold for science and jurisprudence groups. General threshold will be used instead")
    parser.add_argument("--no-journal-drop",
                        dest="journal_drop",
                        action="store_false",
                        help="If included, model will make predictions for misindexed journals that have been shown to be difficult to classify")
    parser.add_argument("--dest",
                        dest="destination",
                        default=".",
                        help="Destination directory for predictions or testing metrics. Will default to the current directory")
    parser.add_argument("--validation",
                        dest="validation",
                        action="store_true")
                        help="If included, test the system on the validation dataset. Will output metrics to classification_predictions.txt")
    parser.add_argument("--test",
                        dest="test",
                        action="store_true")
                        help="If included, test the system on the test dataset. Will output metrics to classification_predictions.txt")

    return parser

def save_predictions(adjusted_predictions, prediction_dict, pmids, destination):
    """
    Save predictions to file in format
    pmid|binary prediction|probability
    """
    
    with open("{}/citation_predictions.txt".format(destination), "w") as f:
        for i, prediction in enumerate(adjusted_predictions):
            f.write("{0}|{1}|{2}\n".format(pmids[i], prediction, prediction_dict['predictions'][i]))

def main():
    """
    Main function to run voting and CNN, combine results,
    adjust decision threshold, and make predictions
    """

    args = get_args().parse_args()
    journal_ids_path = resource_filename(__name__, "models/journal_ids.txt")
    word_indicies_path = resource_filename(__name__, "models/word_indices.txt")

    group_thresh = args.group_thresh
    journal_drop = args.journal_drop
    destination = args.destination

    # Run system on test or validation set if specified
    if args.test or args.validation:
        dataset = "test" if args.test else "validation"
        SIS_test_main(
            dataset, journal_ids_path, word_indicies_path, 
            group_thresh, journal_drop, destination)

    #Otherwise run on batch of citations
    else:
        XML_path = args.path
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
            adjusted_predictions = drop_predictions(prediction_dict, adjusted_predictions, misindexed_ids)
        save_predictions(adjusted_predictions, prediction_dict, pmids, destination)


