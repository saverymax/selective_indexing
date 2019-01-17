"""
Module for verification of performance of system on test or validation data
"""

import json
import argparse
from math import isclose
from sklearn.metrics import classification_report, precision_score, recall_score
import datetime
import pickle

from ..combined_model import *
from ..preprocess_CNN_data import get_batch_data 
from .preprocess_voting_data_test import preprocess_data
from ..misindexed_journal_ids import misindexed_ids


def parse_test_citations(XML_path):
    """
    Parse the test citations 
    that alistair put together
    """
    
    with open(XML_path) as f:
        citations_json = json.load(f) 

    return citations_json


def drop_test_predictions(prediction_dict, adjusted_predictions, labels):
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


def evaluate_individual_models(cnn_predictions, voting_predictions, labels):
    """
    Evaluate the performance on the CNN and voting
    ensemble, using the validation or test data sets. 
    Returns precision and recall for each model.
    """

    cnn_thresh = .02
    voting_thresh = .04

    adj_voting_preds = [1 if y >= voting_thresh else 0 for y in voting_predictions]
    adj_cnn_preds = [1 if y >= cnn_thresh else 0 for y in cnn_predictions]
    voting_precision = precision_score(labels, adj_voting_preds)
    voting_recall = recall_score(labels, adj_voting_preds)
    cnn_precision = precision_score(labels, adj_cnn_preds)
    cnn_recall = recall_score(labels, adj_cnn_preds)

    return cnn_recall, cnn_precision, voting_recall, voting_precision


def SIS_test_main(
        dataset, journal_ids_path, word_indicies_path, 
        group_thresh, journal_drop, destination):
    """
    Main function to run voting and CNN, combine results,
    adjust decision threshold, and make new predictions
    """

    if dataset == "validation":
        XML_path = resource_filename(__name__, "datasets/pipeline_validation_set.json")
    else:
        XML_path = resource_filename(__name__, "datasets/pipeline_test_set")

    citations = parse_test_citations(XML_path) 
    voting_citations, journal_ids, labels = preprocess_data(citations)
    voting_predictions = run_voting(voting_citations)
    CNN_citations = get_batch_data(citations, journal_ids_path, word_indicies_path)
    cnn_predictions = run_CNN(CNN_citations)
    combined_predictions = combine_predictions(voting_predictions, cnn_predictions)
    prediction_dict = {'predictions': combined_predictions, 'journal_ids': journal_ids}
    adjusted_predictions = adjust_thresholds(prediction_dict, group_thresh) 
    if journal_drop:
        adjusted_labels, adjusted_predictions = drop_test_predictions(prediction_dict, adjusted_predictions, labels)
    else:
        adjusted_labels = labels

    cnn_recall, cnn_precision, voting_recall, voting_precision = evaluate_individual_models(cnn_predictions, voting_predictions, labels)
    SIS_recall = recall_score(adjusted_labels, adjusted_predictions)
    SIS_precision = precision_score(adjusted_labels, adjusted_predictions)

    if not group_thresh and not journal_drop:
        if dataset == "validation":
            assert isclose(cnn_recall, .9964, abs_tol=1e-4), "CNN recall does not match expected value"
            assert isclose(cnn_precision, .3312, abs_tol=1e-4), "CNN precision does not match expected value"
            assert isclose(voting_recall, .9956, abs_tol=1e-4), "Voting recall does not match expected value"
            assert isclose(voting_precision, .2899, abs_tol=1e-4), "Voting precision does not match expected value"
            assert isclose(SIS_recall, .9949, abs_tol=1e-4), "SIS recall does not match expected value"
            assert isclose(SIS_precision, .3897, abs_tol=1e-4), "SIS precision does not match expected value"
            print("Assertions passed")
        else:
            assert isclose(cnn_recall, .9948, abs_tol=1e-4), "CNN recall does not match expected value" 
            assert isclose(cnn_precision, .3254, abs_tol=1e-4), "CNN precision does not match expected value"
            assert isclose(voting_recall, .9927, abs_tol=1e-4), "Voting recall does not match expected value"
            assert isclose(voting_precision, .2845, abs_tol=1e-4), "Voting precision does not match expected value"
            assert isclose(SIS_recall, .9923, abs_tol=1e-4), "SIS recall does not match expected value"
            assert isclose(SIS_precision, .3845, abs_tol=1e-4), "SIS precision does not match expected value"
            print("Assertions passed")

    results_path = "{}/SIS_test_results.txt".format(destination)
    with open(results_path, "a") as f:
        f.write("""\n\n{0}\nDataset: {1}\n--no-journal-drop: {2}\n--no-group-thresh {3}\n""".format(
                    datetime.datetime.now(), 
                    dataset,
                    journal_drop,
                    group_thresh
                    ))

        f.write("""SIS recall: {0}\nSIS precision: {1}\nVoting recall: {2}\nVoting precision: {3}\nCNN recall: {4}\nCNN precision: {5}\n""".format(
                    SIS_recall,
                    SIS_precision,
                    voting_recall,
                    voting_precision,
                    cnn_recall,
                    cnn_precision))
