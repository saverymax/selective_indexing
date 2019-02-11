# Selective Indexing System (SIS)

This repository contains the source code for the combination of 
a CNN and voting ensemble in the prediction of citations requiring
MeSH indexing

## Installation

Is anaconda installed? Is python 3.6 installed? If so, then you are good to go. Skip to section ii.
If you do not have anaconda, miniconda, or python installed, follow the instructions in i.

### i
Here are instructions to install miniconda, a lightweight version of anaconda. In installing miniconda, python and 
all standard libraries are included.

First, download the miniconda installer:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

Then run the bash installer you just downloaded. 
```
bash Miniconda3-latest-Linux-x86_64.sh
```
Agree to the demands it makes, and make sure to enter yes when it asks to add the miniconda path to the .bashrc

Remember to restart the terminal. Don't worry, we're almost done... 

Unfortunately python 3.7 is not currently compatible with tensorflow, and since
the latest miniconda comes with python 3.7, we will have to downgrade, until this changes. 
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

To download the .whl file for the SIS package, either click on the release button that should be somewhere up and to the right on github,
or follow this link: https://github.com/saverymax/selective_indexing/releases

Under Assets, click on the SIS-*.*.*-py3-none-any.whl link to download, and we can get started with the installation. 

Assuming you have downloaded the .whl file for the SIS package, navigate to the directory where it lives via shell and enter the command below to install.
```
pip install SIS-*.*.*-py3-none-any.whl
```
If all goes well, you have now installed the Selective Indexing System (SIS). Congratulations!
SIS has been added to PATH, and is executable from the command line. 

Wait! One more thing...
Currently the text is tokenized with the NLTK tokenizer. 
NLTK requires you install it separately. Once you do this once,
you don't have to worry about it again, even if you uninstall and 
reinstall SIS. To install:
``` 
python -m nltk.downloader punkt
```

That's it for the install! 

If you should, for some strange reason, want to uninstall the package, enter
```
pip uninstall SIS
```

## Usage

To run the system from the command line, enter
```
SIS --path path/to/some_citations.xml
```
For example, if sample_citations.xml is in your current directory, running
```
SIS --path sample_citations.xml
```
will generate a set of predictions for the two citations in sample_citations.xml

By default, the system will iterate through the citations, and make predictions 
for each citation published by a selectively indexed journal recommended as important,
that does not have a status of MEDLINE or PubMed-not-MEDLINE. 
The prediction results can be found in the citation_predictions_YYYY-DD-MM.txt output file, which will by default
be saved in your current directory. Each prediction is printed on a line, and the format is 
pmid|binary prediction|probability. 

For journals that have, in the past, been misindexed and are among those that
we have shown to significantly detract from performance, no prediction will be provided. 

### Command line options:
As of version 0.1.1, 7 options are available. 

**--path** 
    \nPath to XML of citations for the system to classify. Include the file.xml in the path. 
    Do not include with --test or --validation

**--group-thresh**
    \nOptional. If included, the system will use the unique, 
    predetermined thresholds for citations from journals in the science or jurisprudence category. Originally, this was intended to improve performance; however, it was shown to be difficult to apply a threshold chosen on the validation set to the test set.

**--no-journal-drop**
    \nOptional. By defualt the system does not make predictions for a small set of journals previously misindexed. This has been shown to improve system performance. To make predictions all citations, including those from these journals, include this option. 
    Important to note, this option only has an effect when --predict-medline is not included.

**--dest dir/for/results/** 
    \nOptional. Destination for predictions, or test results if --test or --validation are used. Defaults to 
    current directory. File names for predictions or test results are hardcoded, for now: 
    citation_predictions_YYYY-DD-MM.txt if running system on a batch of citations; SIS_test_results.txt 
    if running on test or validation datasets.   

**--validation** 
    \nOptional. Include to run system on 2018 validation dataset. Do not include --path if
    --validation included.  

**--test**
    \nOptional. Include to run system on 2018 test dataset. Do not include --path if
    --test included. 

**--predict_medline**
    \nOptional. New in version 0.1.1. If included, the system will make predictions for 
    ONLY non-selectively indexed journals, with ONLY MEDLINE statuses. 
    Important to note, is that without this option, 
    the system only makes predictions for selectively 
    indexed journals (those recommended to us by human indexers) 
    where the status is not MEDLINE or PubMed-not-MEDLINE. The reason 
    for this switch is to be able to test the performance of the system 
    on citations labeled is MEDLINE, and to also be able to use the system 
    in production, where it is only required to make predictions for selectively 
    indexed citations where the status in PubMed is not yet known.

If you forget your options, input
```
SIS --help
```
and you'll get a little help.

Usage of --validation and --test will be explained below

## Testing
To measure performance of the system, validation and test datasets are included with the SIS
package. To run the models on these datasets, include the --validation or --test option,
as shown in the example below. Input one or the other, not both. These tests are not affected
by the --predict-medline option

For example:
```
SIS --validation --dest path/to/output/
```
This will output a performance report into the file SIS_test_results.txt in the output directory. 
It is not necessary to include the --path option when running these tests. 
For a given test the following information is appended to the SIS_test_results.txt file:

Date
All command line keywords and values
SIS recall
SIS precision
Voting recall
Voting precision
CNN recall
CNN precision

Once the program is installed run both of the following commands: 
```
SIS --validation --no-journal-drop 
```
and
```
SIS --test --no-journal-drop 
```
If --no-journal-drop is included, a set of assertions 
will be tested on the model's performance. If the assertions are passed,
you can be fairly confident that SIS has been installed correctly and is ready for 
further use.

Further functional testing can be performed using the pytest package.
```
pip install pytest
pytest --pyargs SIS
```
This will run a set of unittests.

Happy indexing.





