"""
Verify performance of system on test data
"""

import json
import lxml.etree as le
import argparse
from sklearn.metrics import classification_report
import datetime

from ..combined_model import *
from ..preprocess_CNN_data import get_batch_data 
from .preprocess_voting_data_test import preprocess_data
from .incongruous_citations import incongruous_citations
from ..misindexed_journal_ids import misindexed_ids
from .. import item_select

def get_args():
    """
    Get command line parser
    """

    parser = argparse.ArgumentParser(description="Arguments for initializing classifier")
    parser.add_argument("--validation",
                        dest="validation",
                        action="store_true",
                        help="If included, use validation set. Otherwise, the results will be for test set")
    parser.add_argument("--no-group-thresh",
                        dest="group_thresh",
                        action="store_false",
                        help="If included, do not use predetermined threshold for science and jurisprudence groups. Otherwise, experiment will be run on test set")
    return parser

def remove_citations(citations):
    """
    Remove the 34 citations that were in Alistair's test
    set that were not in mine
    """

    filtered_citations = [citation for citation in citations if citation['pmid'] not in incongruous_citations] 

    return filtered_citations
        
def parse_test_citations(XML_path):
    """
    Parse the test citations 
    that alistair put together
    """
    
    with open(XML_path) as f:
        citations_json = json.load(f) 

    return citations_json

def drop_predictions(prediction_dict, adjusted_predictions, labels):
    """
    Drop predictions of citations from 
    misindexed citations
    """

    filtered_predictions = []
    filtered_labels = []
    
    for i, journal_id in enumerate(prediction_dict['journal_ids']):
        if journal_id not in misindexed_ids:
            filtered_labels.append(labels[i])
            filtered_predictions.append(adjusted_predictions[i])

    return filtered_labels, filtered_predictions
    
def main(XML_path, journal_ids_path, word_indicies_path, group_thresh):
    """
    Main function to run voting and CNN, combine results,
    adjust decision threshold, and make new predictions
    """
    
    citations = parse_test_citations(XML_path) 
    citations = remove_citations(citations)
    voting_citations, journal_ids, labels = preprocess_data(citations)
    voting_predictions = run_voting(voting_citations)
    CNN_citations = get_batch_data(citations, journal_ids_path, word_indicies_path)
    cnn_predictions = run_CNN(CNN_citations)
    combined_predictions = combine_predictions(voting_predictions, cnn_predictions)
    prediction_dict = {'predictions': combined_predictions, 'journal_ids': journal_ids}
    adjusted_predictions = adjust_thresholds(prediction_dict, group_thresh) 
    labels, adjusted_predictions = drop_predictions(prediction_dict, adjusted_predictions, labels)
    
    results_path = ["selective_indexing_system", "tests", "test_results", "SIS_test_results.txt"]
    results_path = Path.cwd().joinpath(*results_path)
    with open(results_path, "a") as f:
        f.write("\n{0}\n{1}\n".format(datetime.datetime.now(), classification_report(labels, adjusted_predictions)))

if __name__ == "__main__":
    args = get_args().parse_args()
    if args.validation:
        XML_path = "selective_indexing_system/tests/datasets/pipeline_validation_set.json"
    else:
        XML_path = "selective_indexing_system/tests/datasets/pipeline_test_set"

    journal_ids_path = "selective_indexing_system/models/journal_ids.txt"
    word_indices_path = "selective_indexing_system/models/word_indices.txt"
    main(XML_path, journal_ids_path, word_indices_path, args.group_thresh)
