# langid utilities

langid is used for identifying which language a string likely is, while
it comes with a large number of languages, this naturally does not
include languages like sanskrit and pali. Also, even for english, the
default training texts are of a different nature to buddhist translations,
for the best possible identification of buddhist hybrid english and such, 
along with the ability to identify pali, sanskrit, etc, we generate
a custom model using exactly the texts people will be searching.


langid training tools use python2.7, so this this folder should be 
setup with a python2.7 virtual environment:

## Setup 2.7.9 environment using pyenv
i.e. with python

pyenv install 2.7.9
pyenv virtualenv 2.7.9 langid
pyenv local langid

Install numpy into the virtualenv

pip install numpy

## Set up folder
From the langid package, extract the "train" subfolder into this folder,
so it looks like:
utility/langid/train


## Generate Corpus
The corpus generating python script runs in the usual suttacentral 
environment, to do this simply run the script `generate_langid_corpus.py`
in the utility folder. This will create the langid/corpus folder.

## Generate Model

finally run the script in this folder:

make_model.sh

It will take quite a while to run and will create a model file, which
can be used with langid.py
