# Robot Awareness --- PC

## Version information
- Python 3.6.2

## Core APIs used
1. Watson Natural Language Understand [link](https://natural-language-understanding-demo.ng.bluemix.net/)
2. Standford Temporal Tagger SUTime [link](https://nlp.stanford.edu/software/sutime.shtml)
3. Dialogue Act Tagger [link](https://github.com/ColingPaper2018/DialogueAct-Tagger)

## Dependencies, requirements, and APIs
#### 1. Install python packages
```
$ pip install -r requirements.txt
```

#### 2. Get apache maven
Apache Maven `mvn` is required to install all SUTime java dependencies.
- [download](https://maven.apache.org/download.cgi)
- [install](https://maven.apache.org/install.html)
Run the following command upon successful installation.
```
$ mvn dependency:copy-dependencies -DoutputDirectory=./jars
```

#### 3. Get Required API keys
API keys from the following IBM Watson services are required to run the program. Obtain your API keys from the following links and set all the required values in the `dot.env` file provided. Rename the file to `.env` following that.
1. Watson Tone Analyzer [link](https://cloud.ibm.com/apidocs/tone-analyzer)
2. Watson Natural Language Understanding [link](https://cloud.ibm.com/apidocs/natural-language-understanding)


## Troubleshooting problematic dependencies
| Dependencies | Solution |
| ------------- | ------------- |
| pip install `sutime` | [link to stackoverflow solution](https://stackoverflow.com/questions/14372706/visual-studio-cant-build-due-to-rc-exe) <br> [link to sutime full setup](https://github.com/FraBle/python-sutime) |
| pip install `cytoolz`  | install using `.whl` file <br> i.e. `pip install whl/cytoolz-0.9.0.1-cp36-cp36m-win_amd64.whl` |
| pip install `ujson`  | install using `.whl` file <br> i.e. `pip install whl/ujson-1.35-cp36-cp36m-win_amd64.whl` |
