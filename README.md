# Biomedical Citation Selector (BmCS)

This repository contains the source code for the BmCS system, to be used for the prediction of citations requiring MeSH indexing

## Installation

Is anaconda or miniconda installed? Is python 3.6 installed? If so, then you are good to go. Skip to section ii.
If you do not have anaconda, or miniconda, and python installed, follow the instructions in i.

Note that this package requires python 3.6.

### i
Here are instructions to install miniconda, a lightweight version of anaconda. In installing miniconda, python and 
standard libraries are included.

First, download the miniconda installer:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

Then run the bash installer you just downloaded. 
```
bash Miniconda3-latest-Linux-x86_64.sh
```
Agree to its demands, and make sure to enter yes when it asks to add the miniconda path to the .bashrc

Remember to restart the terminal or source the bashrc. Don't worry, we're almost done... 

Unfortunately python 3.7 is not currently compatible with tensorflow 1.11.0, the version used in this system.
Since the latest miniconda comes with python 3.7 (as of March 2019), we will have to downgrade.
Fortunately, this is easy:
```
conda install python=3.6
```

Finally, check your python version. 
```
python --version
```

If python == 3.6, continue on to section ii. If not, return to go, and maybe email someone for help.

### ii

To download the .whl file for the BmCS package, either click on the release button that should be somewhere up and to the right on github,
or follow this link: https://github.com/saverymax/selective_indexing/releases

Under Assets, click on the BmCS-0.1.1-py3-none-any.whl link to download, and we can get started with the installation. 

Assuming you have downloaded the .whl file for the BmCS package, navigate to the directory where it lives and enter the command below to install.
```
pip install BmCS-0.1.1-py3-none-any.whl
```
If all goes well, you have now installed the Biomedical Citation Selector (BmCS). Congratulations!
BmCS has been added to PATH, and is executable from the command line. 

Wait! One more thing...
Currently the text is tokenized with the NLTK tokenizer. 
NLTK requires you install it separately. Once you do this once,
you don't have to worry about it again, even if you uninstall and 
reinstall BmCS. To install:
``` 
python -m nltk.downloader punkt
```

To uninstall
```
pip uninstall BmCS
```

## Usage

The models are not included in this version of the system. The path should be provided in the command line options.

To run the system BmCS the command line
```
BmCS --path path/to/some_citations.xml --ensemble-path /path/to/model.joblib --cnn-path /path/to/cnn/weights.hdf5 --predict-all
```
For example, if sample_citations.xml is in your current directory and the models are in a models diretory also in your current directory
```
BmCS --path sample_citations.xml --ensemble-path ./models/ensemble.joblib --cnn-path ./models/model_CNN_weights.hdf5 --predict-all
```
will generate a set of predictions for the citations in sample_citations.xml

By default, the system will iterate through the citations, and make predictions 
for each citation published by a selectively indexed journal that 
does not have a status of MEDLINE or PubMed-not-MEDLINE. 
The prediction results can be found in the citation_predictions_YYYY-DD-MM.txt output file, which will 
be saved in your current directory, unless otherwise specified. 
Each prediction is printed on a line, in the format 
pmid|prediction|probability|NLM journal ID 

In the prediction field, 4 labels are possible:
0: Out-of-scope for indexing, 99.5% confidence
1: In-scope for indexing, 97% confidence
2: Citation should be human-reviewed. 
3: Citation marked as one of the publication types specified in the publication_types file. This label is off by default and is controlled by --pubtype-filter


### Command line options:
As of version 0.1.2, 8 options are available. 

**--path** 
    Path to XML of citations for the system to classify. Include the file.xml in the path. 
    Do not include with --test or --validation

**--cnn_path** 
    Path to CNN weights.  

**--ensemble_path** 
    Path to ensemble model

**--dest dir/for/results/** 
    Optional. Destination for predictions, or test results if --test or --validation are used. Defaults to 
    current directory. File names for predictions or test results are hardcoded, for now: 
    citation_predictions_YYYY-DD-MM.txt if running system on a batch of citations; BmCS_test_results.txt 
    if running on test or validation datasets.   

**--predict-all**
    Optional. If included, system will make predictions 
    for all citations in XML provided, regardless of MEDLINE status or selective indexing status of a given journal. 
    If this option is not included, the system will switch to behavior intended for use outside of NCBI pipeline, i.e., it will filter for selective indexing designation of journal, publication type, and indexing status.

**--pubtype-filter**
    Optional. Modified from version 0.2.1. If included, the system will mark citations with publication types specified in publication_type file with a 3 in the output file. 
    By default this behavior is off, and is overridden by predict-all.
 
**--group-thresh**
    Optional. If included, the system will use the unique, 
    predetermined thresholds for citations from journals in the science or jurisprudence category. Originally, this was intended to improve performance; however, it was shown to be difficult to apply a threshold chosen on the validation set to the test set.

**--journal-drop**
    Optional. By default the system makes predictions for a small set of journals previously misindexed. Include this option to not include those predictions in the output. This has been shown to improve system precision.
    Important to note, this option has no effect when using --predict-all or --predict-medline. 

**--predict-medline**
    Optional. If included, the system will make predictions for 
    ONLY non-selectively indexed journals, with ONLY MEDLINE statuses. 
    Important to note, is that without this option, 
    the system only makes predictions for selectively 
    indexed journals (those recommended to us by human indexers) 
    where the status is not MEDLINE or PubMed-not-MEDLINE. The reason 
    for this switch is to be able to test the performance of the system 
    on citations labeled is MEDLINE, and to also be able to use the system 
    in production, where it is only required to make predictions for selectively 
    indexed citations where the status in PubMed is not yet known.
    This option is overridden by predict-all

**--validation** 
    Optional. Include to run system on 2018 validation dataset. Do not include --path if
    --validation included.  

**--test**
    Optional. Include to run system on 2018 test dataset. Do not include --path if
    --test included. 

If you forget your options, input
```
BmCS --help
```
and you'll get a little help.

Usage of --validation and --test will be explained below


## Testing
To measure performance of the system, validation and test datasets are included with the BmCS
package. To run the models on these datasets, include the --validation or --test option,
as shown in the example below. Input one or the other, not both. These tests are not affected
by the --predict-medline option

For example:
```
BmCS --validation --dest path/to/output/
```
This will output a performance report into the file BmCS_test_results.txt in the output directory. 
It is not necessary to include the --path option when running these tests. 
For a given test the following information is appended to the BmCS_test_results.txt file:

Date
All command line keywords and values
BmCS recall
BmCS precision
Voting recall
Voting precision
CNN recall
CNN precision

Once the program is installed run both of the following commands: 
```
BmCS --validation
```
and
```
BmCS --test
```
If no options are included, a set of assertions 
will be tested on the model's performance. If the assertions are passed,
you can be fairly confident that BmCS has been installed correctly and is ready for 
further use. If options such as journal-drop are included, no assertions will be run,
but the system's performance can still be observed in the test results.

Further functional testing can be performed using the pytest package.
```
pip install pytest
pytest --pyargs BmCS
```
This will run a set of unittests.

Happy indexing.
