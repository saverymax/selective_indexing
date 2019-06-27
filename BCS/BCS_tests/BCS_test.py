"""
Module for verification of performance of system on test or validation data
"""

import json
import argparse
from math import isclose
from sklearn.metrics import classification_report, precision_score, recall_score
import datetime
import pickle
import sys

from ..combined_model import *
from ..preprocess_CNN_data import get_batch_data 
from .preprocess_voting_data_test import preprocess_data
from ..misindexed_journal_ids import misindexed_ids
from ..thresholds import *


def parse_test_citations(XML_path, journal_drop):
    """
    Parse the test citations 
    that alistair put together
    """
    
    with open(XML_path) as f:
        citations = json.load(f) 

    if journal_drop:
        citations = [citation for citation in citations if citation['journal_nlmid'] not in misindexed_ids]

    return citations


def drop_test_predictions(prediction_dict, adjusted_predictions, labels):
    """
    DEPRECATED? 
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


def evaluate_individual_models(cnn_predictions, voting_predictions, labels, group_thresh, journal_ids, group_ids):
    """
    Evaluate the performance on the CNN and voting
    ensemble, using the validation or test data sets. 
    Returns precision and recall for each model.
    """

    if not group_thresh:
        adj_voting_preds = [1 if y >= VOTING_THRESH else 0 for y in voting_predictions]
        adj_cnn_preds = [1 if y >= CNN_THRESH else 0 for y in cnn_predictions]
    # Not working as expected, as validation thresholds don't apply to test set.
    else:
        adj_voting_preds = []
        adj_cnn_preds = []
        for cnn_prob, voting_prob, journal_id in zip(cnn_predictions, voting_predictions, journal_ids):
            if journal_id in group_ids['science']:
                adj_voting_preds.append(1 if voting_prob >= VOTING_SCIENCE_THRESH else 0)
                adj_cnn_preds.append(1 if cnn_prob >= CNN_SCIENCE_THRESH else 0)
            elif journal_id in group_ids['jurisprudence']:
                adj_voting_preds.append(1 if voting_prob >= VOTING_JURISPRUDENCE_THRESH else 0)
                adj_cnn_preds.append(1 if cnn_prob >= CNN_JURISPRUDENCE_THRESH else 0)
            else:
                adj_voting_preds.append(1 if voting_prob >= VOTING_THRESH else 0)
                adj_cnn_preds.append(1 if cnn_prob >= CNN_THRESH else 0)

    voting_precision = precision_score(labels, adj_voting_preds)
    voting_recall = recall_score(labels, adj_voting_preds)
    cnn_precision = precision_score(labels, adj_cnn_preds)
    cnn_recall = recall_score(labels, adj_cnn_preds)

    return cnn_recall, cnn_precision, voting_recall, voting_precision


def BCS_test_main(
        dataset, journal_ids_path, word_indicies_path, 
        group_thresh, journal_drop, destination, group_ids, args):
    """
    Main function to run voting and CNN, combine results,
    adjust decision threshold, and make new predictions
    """

    if dataset == "validation":
        XML_path = resource_filename(__name__, "datasets/pipeline_validation_set.json")
    else:
        XML_path = resource_filename(__name__, "datasets/pipeline_test_set")
   
    citations = parse_test_citations(XML_path, journal_drop) 
    voting_citations, journal_ids, labels = preprocess_data(citations)
    voting_predictions = run_voting(voting_citations)
    CNN_citations = get_batch_data(citations, journal_ids_path, word_indicies_path)
    cnn_predictions = run_CNN(CNN_citations)
    combined_predictions = combine_predictions(voting_predictions, cnn_predictions)
    prediction_dict = {'predictions': combined_predictions, 'journal_ids': journal_ids}
    adjusted_predictions = adjust_thresholds(prediction_dict, group_thresh) 

    cnn_recall, cnn_precision, voting_recall, voting_precision = evaluate_individual_models(cnn_predictions, voting_predictions, labels, group_thresh, journal_ids, group_ids)
    BCS_recall = recall_score(labels, adjusted_predictions)
    BCS_precision = precision_score(labels, adjusted_predictions)

    # Values computed using generate_validation_vs_test_vs_group_thresholds.py
    if not group_thresh and not journal_drop:
        if dataset == "validation":
            assert isclose(cnn_recall, .9952, abs_tol=1e-4), "CNN recall does not match expected value"
            assert isclose(cnn_precision, .3508, abs_tol=1e-4), "CNN precision does not match expected value"
            assert isclose(voting_recall, .9952, abs_tol=1e-4), "Voting recall does not match expected value"
            assert isclose(voting_precision, .3030, abs_tol=1e-4), "Voting precision does not match expected value"
            assert isclose(BCS_recall, .9952, abs_tol=1e-4), "BCS recall does not match expected value"
            assert isclose(BCS_precision, .3858, abs_tol=1e-4), "BCS precision does not match expected value"
            print("Assertions passed")
        else:
            assert isclose(cnn_recall, .9946, abs_tol=1e-4), "CNN recall does not match expected value" 
            assert isclose(cnn_precision, .3459, abs_tol=1e-4), "CNN precision does not match expected value"
            assert isclose(voting_recall, .9931, abs_tol=1e-4), "Voting recall does not match expected value"
            assert isclose(voting_precision, .2998, abs_tol=1e-4), "Voting precision does not match expected value"
            assert isclose(BCS_recall, .9935, abs_tol=1e-4), "BCS recall does not match expected value"
            assert isclose(BCS_precision, .3795, abs_tol=1e-4), "BCS precision does not match expected value"
            print("Assertions passed")

    results_path = "{}/BCS_test_results.txt".format(destination)
    with open(results_path, "a") as f:
        f.write("\n\n")
        for arg in vars(args):
            f.write("{0}: {1}\n".format(arg, vars(args)[arg]))
        f.write("""BCS recall: {0}\nBCS precision: {1}\nVoting recall: {2}\nVoting precision: {3}\nCNN recall: {4}\nCNN precision: {5}\n""".format(
                BCS_recall,
                BCS_precision,
                voting_recall,
                voting_precision,
                cnn_recall,
                cnn_precision))
