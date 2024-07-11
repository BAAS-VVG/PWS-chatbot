# PWS-chatbot

Install the language model with:

python -m spacy download en_core_web_sm

If this doesn't work, replace the 'python' with the specific location of the python executable that is being used for the project, like so:

'~/AppData/Local/Programs/Python/Python39/python.exe' -m spacy download en_core_web_sm

Run the system with:

python3 project.py

The answers will be saved in answers.txt.


Additionally, question files can be used as input by calling:

python3 project.py < inputfile

