#!/bin/bash

python ./train/index.py ./corpus

python ./train/tokenize.py corpus.model

python ./train/DFfeatureselect.py corpus.model

python ./train/IGweight.py -d corpus.model
python ./train/IGweight.py -lb corpus.model

python ./train/LDfeatureselect.py corpus.model

python ./train/scanner.py corpus.model

python ./train/NBtrain.py corpus.model

echo "Done! Find the model under ./corpus.model/model"
