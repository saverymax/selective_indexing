import numpy as np
from pathlib import Path
import time
from pkg_resources import resource_string, resource_filename

import keras.backend as K
from keras.models import model_from_json

from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import classification_report

from .embedding_custom import EmbeddingWithDropout
from .group_ids import science, jurisprudence
from . import item_select

def get_args():
    """
    Get command line arguments
    """
    parser.add_argument("-e",
                        default="Run trained voting model",
                        dest="experiment",
                        help="Input details of experiment")
    parser.add_argument("-f",
                        dest="predictions_file",
                        help="Input title of csv in which predictions will be saved")
    return parser

def run_CNN(X):
    """
    load the CNN and return predictions
    """

    print("Making CNN predictions")
    model_path = resource_filename(__name__, "models/model_CNN.json")
    weights_path = resource_filename(__name__, "models/model_CNN_weights.hdf5")

    with open(model_path, 'rt') as model_json_file:
        model_json = model_json_file.read()

    model = model_from_json(model_json, custom_objects={EmbeddingWithDropout.__name__: EmbeddingWithDropout})
    model.load_weights(weights_path)
    model.compile(loss='binary_crossentropy', optimizer='adam')
    result = model.predict(X).flatten()

    return result

def run_voting(X):
    """
    Run the voting model
    """

    print("Making voting predictions")
    model_path = resource_filename(__name__, "models/voting_recall_no_bad_journals_2017_data_model_tfidf_all_journals.joblib")
    model = joblib.load(model_path)
    y_probs = model.predict_proba(X)[:, 0]

    return y_probs

def adjust_thresholds(predictions_dict, group_thresh=True):
    """
    Adjust threshold depending on the category of the journal 
    """

    print("Combining predictions")
    COMBINED_THRESH = .0045
    SCIENCE_THRESH = .02 
    JURISPRUDENCE_THRESH = .1 
    
    if not group_thresh:
        return [1 if y >= COMBINED_THRESH else 0 for y in predictions_dict['predictions']]
    
    else:
        predictions = []
        for y, journal_id in zip(predictions_dict['predictions'], predictions_dict['journal_ids']):
            if journal_id in science:
                predictions.append(1 if y>= SCIENCE_THRESH else 0)
            elif journal_id in jurisprudence:
                predictions.append(1 if y>= JURISPRUDENCE_THRESH else 0)
            else:
                predictions.append(1 if y>= COMBINED_THRESH else 0)
        return predictions

def combine_predictions(voting_predictions, cnn_predictions):
    """
    Combine the predictions of the two models
    """

    return voting_predictions*cnn_predictions

def drop_predictions(prediction_dict, adjusted_predictions, misindexed_ids):
    """
    Convert predictions of citations from 
    misindexed citations to N/A
    """

    for i, journal_id in enumerate(prediction_dict['journal_ids']):
        if journal_id in misindexed_ids:
            adjusted_predictions[i] = "N/A" 

    return adjusted_predictions


