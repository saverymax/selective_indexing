# Selective Indexing System (SIS)

This repository contains the source code for the combination of 
a CNN and voting ensemble in the prediction of citations requiring
MeSH indexing

## Installation

Is anaconda installed? Is python 3.6 installed? If so, then you are good to go. Skip to section installation.ii.
If you do not have anaconda, miniconda, or python installed, follow the instructions in installation.i.

###i
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

Unfortunately python 3.7 is not compatible with tensorflow, and since
the latest miniconda comes with python 3.7, we will have to downgrade. Fortunately, this is easy:
```
conda install python=3.6
```

Finally, check your python version. 
```
python --version
```

If python == 3.6, continue on to section ii. If not, return to go.

###ii

Assuming you have downloaded the .whl file, navigate to the directory where it lives and enter the command below to install.
```
pip install SIS-0.*.*-py3-none-any.whl
```
If all goes well, you have now installed the Selective Indexing System (SIS). Congratulations!
SIS has been added to PATH, and is executable from the command line. 

If you should, for some strange reason, want to uninstall the package, enter
```
pip uninstall SIS
```

## Usage

To run the system from the command line, enter
```
SIS --path path/to/some_citations.xml
```
alternatively, this will work
```
python -m SIS --path path/to/some_citations.xml
```

For example, if sample_citations.xml is in your current directory, running
```
SIS --path sample_citations.xml
```
will generate a set of predictions for the two citations in sample_citations.xml

### Command line options:
As of version 0.0.1, 6 options are available. 

**--path** 
    Path to XML of citations for the system to classify. Include the file.xml in the path. 
    Do not include with --test or --validation

**--no-group-thresh**
    Optional. If included, the system will use the same threshold for all citations, 
    no matter the journal of origin. Without this flag, the system will use unique, 
    predetermined thresholds for citations from journals in the science or 
    jurisprudence category, improving system performance.

**--no-journal-drop**
    Optional. If included, the models will use the same threshold for all citations, 
    no matter the journal of origin. Without this flag, the system will use unique, 
    predetermined thresholds for citations from journals in the science or 
    jurisprudence category, improving system performance.

**--dest dir/for/results/** 
    Optional. Destination for predictions, or test results if --test or --validation are used. Defaults to 
    current directory. File names for predictions or test results are hardcoded, for now: 
    citation_predictions.txt if running system on a batch of citations; SIS_test_results.txt 
    if running on test or validation datasets.   

**--validation** 
    Optional. Include to run system on 2018 validation dataset. Do not include --path if
    --test included.  

**--test**
    Optional. Include to run system on 2018 test dataset. Do not include --path if
    --valiation included. 

If you forget your options, input
```
SIS --help
```
and you'll get a little help.

Usage of --validation and --test will be explained below

## Testing
To measure performance of the system, validation and test datasets are included with the SIS
package. To run the models on these datasets, include the --validation or --test option
as shown in the example below. Input one or the other, not both. 

For example:
```
SIS --validation --dest path/to/output/
```
This will output a performance report into the file SIS_test_results.txt in the output directory. 
It is not necessary to include the --path option when running these tests. 

Once the program is installed run both of the following commands: 
```
SIS --validation --no-journal-drop --no-group-thresh
```
and
```
SIS --test --no-journal-drop --no-group-thresh
```
If --no-journal-drop and --no-group-thresh are included, a set of assertions 
will be tested on the model's performance. If the assertions are passed,
you can be fairly confident that SIS has been installed correctly and is ready for 
further use.

Happy indexing.





