import argparse
import sys
import json
import datetime
from pkg_resources import resource_string
import unittest
from unittest.mock import patch

from ..combined_model import *
from ..daily_update_file_parser import parse_update_file
from ..preprocess_CNN_data import get_batch_data 
from ..preprocess_voting_data import preprocess_data
from ..SIS_tests.SIS_test import SIS_test_main

class test_SIS_cli(unittest.TestCase):
    """
    Class to test 
    the effect of command line arguments on input to models
    Primarily this is to make sure journal dropping things 
    in the daily_update_parser work as expected,
    especially as more things are added on
    """

    def get_args(self):
        """
        Get command line parser
        """

        parser = argparse.ArgumentParser(description="Arguments for initializing classifier")
        parser.add_argument("--path",
                            dest="path",
                            help="Path to XML containing batch of citations")
        parser.add_argument("--group-thresh",
                            dest="group_thresh",
                            action="store_true",
                            help="If included, use predetermined threshold for science and jurisprudence groups. Default is to not use these group thresholds, as they have been shown hard to predict.")
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
                            action="store_true",
                            help="If included, test the system on the validation dataset. Will output metrics to SIS_test_results.txt")
        parser.add_argument("--test",
                            dest="test",
                            action="store_true",
                            help="If included, test the system on the test dataset. Will output metrics to SIS_test_results.txt")
        parser.add_argument("--predict-medline",
                            dest="predict_medline",
                            action="store_true",
                            help="If included, the system will make predictions for all citations.  If not included, it will only make predictions for citations from selectively indexed journals that have been suggested to be important")

        return parser

    def save_predictions(self, adjusted_predictions, prediction_dict, pmids, destination):
        """
        Save predictions to file in format
        pmid|binary prediction|probability

        Currently not used for testing
        """

        with open("{0}/citation_predictions_{1}.txt".format(destination, datetime.datetime.now().strftime('%Y-%m-%d')), "w") as f:
            for i, prediction in enumerate(adjusted_predictions):
                f.write("{0}|{1}|{2}\n".format(pmids[i], prediction, prediction_dict['predictions'][i]))

    def test_main(self):
        """
        Main function to run voting and CNN, combine results,
        adjust decision threshold, and make predictions
        """

        # Use unitttest.mock.patch to simulate command line arguments, so that they can be used 
        # with pytest
        # Good SO answer:
        # https://stackoverflow.com/questions/18160078/how-do-you-write-tests-for-the-argparse-portion-of-a-python-module
        with patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
                                path="null",
                                group_thresh=False,
                                journal_drop=True,
                                destination=".",
                                validation=False,
                                test=False,
                                predict_medline=False
                                )):
            args = self.get_args().parse_args()

        journal_ids_path = resource_filename(__name__, "../models/journal_ids.txt")
        word_indicies_path = resource_filename(__name__, "../models/word_indices.txt")
        
        selectively_indexed_id_path = resource_filename(__name__, "../selectively_indexed_id_mapping.json")
        with open(selectively_indexed_id_path, "r") as f:
            selectively_indexed_ids = json.load(f)
     
        group_id_path = resource_filename(__name__, "../group_ids.json") 
        with open(group_id_path, "r") as f:
            group_ids = json.load(f)

        group_thresh = args.group_thresh
        journal_drop = args.journal_drop
        destination = args.destination
        predict_medline = args.predict_medline
        
        # Ids of citations in test_citations.xml.
        # The ids have been hand selected, for their status and indexing status,
        # so that their treatment by the system can be predicted.
        test_ids = [
                "12269810", # MEDLINE status, from non-selectively indexed journal
                "21179314", # PubMed-not-MEDLINE status, from non-selectively indexed journals
                "30568209", # In process status, from selectively indexed journal
                "29994383", # In process status, from selectively indexed journal in journal drop list
                ]
                    
        XML_path = resource_filename(__name__, "datasets/test_citations.xml")
        self.assertEqual(journal_drop, True)
        self.assertEqual(predict_medline, False)
        # Run on citations curated for testing command line options
        # All dropping options are considered in parse_update_file
        # First run with default, where journal_drop == True and predict_medline == False
        citations = parse_update_file(XML_path, journal_drop, predict_medline, selectively_indexed_ids)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]['pmid'], int(test_ids[2]))

        # Then set journal drop to false:
        journal_drop = not journal_drop
        citations = parse_update_file(XML_path, journal_drop, predict_medline, selectively_indexed_ids)
        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0]['pmid'], int(test_ids[2]))
        self.assertEqual(citations[1]['pmid'], int(test_ids[3]))
        
        # And then try with predict_medline as true. 
        predict_medline = not predict_medline
        citations = parse_update_file(XML_path, journal_drop, predict_medline, selectively_indexed_ids)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]['pmid'], int(test_ids[0]))

        # Test length and type of data + predictions
        voting_citations, journal_ids, pmids = preprocess_data(citations)
        self.assertIsInstance(voting_citations, dict)
        for key in voting_citations:
            self.assertIsInstance(voting_citations[key], list)
        voting_predictions = run_voting(voting_citations)
        self.assertEqual(len(voting_predictions), len(citations))
        CNN_citations = get_batch_data(citations, journal_ids_path, word_indicies_path)
        self.assertIsInstance(CNN_citations, dict)
        for key in CNN_citations:
            if key == "pmids":
                self.assertIsInstance(CNN_citations[key], list)
            else:
                self.assertIsInstance(CNN_citations[key], np.ndarray)
        cnn_predictions = run_CNN(CNN_citations)
        self.assertEqual(len(cnn_predictions), len(citations))
        combined_predictions = combine_predictions(voting_predictions, cnn_predictions)
        self.assertEqual(len(combined_predictions), len(citations))
        prediction_dict = {'predictions': combined_predictions, 'journal_ids': journal_ids}
        self.assertEqual(len(prediction_dict['predictions']), len(prediction_dict['journal_ids']))
        adjusted_predictions = adjust_thresholds(prediction_dict, group_thresh) 
        self.assertEqual(len(combined_predictions), len(adjusted_predictions))
        self.save_predictions(adjusted_predictions, prediction_dict, pmids, destination)

