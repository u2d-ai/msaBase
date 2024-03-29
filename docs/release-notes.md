# msaBase Release Notes
## Possible future features:

## 0.0.136

- change auto offset reset to latest

## 0.0.135

- fix logging and create message for Kafka
- update msaDocModels version

## 0.0.134

- Updated sending messages to Kafka

## 0.0.133

- Add not create consumers if the service works without Kafka.

## 0.0.132

- update msaDocModels

## 0.0.131

- fix interrapting 

## 0.0.130

- fixed default params for kafka auth

# 0.0.129

- Extended configuration for producer and consumer configs with env vars

# 0.0.128

- remove close()

# 0.0.127

- fix process hangs after sending a message

# 0.0.126

- fix interrapting kafka thread

# 0.0.125

- fix deserialize message from kafka


# 0.0.124

- update info pub logger

# 0.0.123

- remove dapr
- remove redis pubsub
- add kafka

# 0.0.122

- update msaDocModels

# 0.0.121

- update msaDocModels

# 0.0.120

- update msaDocModels with svcEngineUtils models

# 0.0.119

- fix dependencies

# 0.0.118

- fix dependencies

# 0.0.117

- update msaDocModels

# 0.0.116

- add svcConverterSeparation models for processing documents.


# 0.0.115

- add working to receive default message from pub/sub
- update setup file, add lock file

# 0.0.114

- migrate to poetry

# 0.0.113

- change SeparationInferenceDTO
- add patterns to ConverterEmail

# 0.0.112

- fix Barcode model

# 0.0.111

- add models for ConvertorSeparation and models for document Taxonomy

# 0.0.109

- add Input and DTO models for Spellcheck

# 0.0.108

- added enviroments for sentry

## 0.0.107

- fix algorithm to DocClassifier Input

# 0.0.106

- add possibility to update dapr component names from env
- add algorithm to DocClassifier Input
- change dto model for DocClassifier

# 0.0.105

- updated msaDocModels

# 0.0.104

- add Enum with Keywords algorithms

# 0.0.103

- pinned anyio library

# 0.0.102

- updated msaDocModels

# 0.0.101

- updated msaDocModels

# 0.0.100

- updated msaDocModels

# 0.0.99

- updated msaDocModels

# 0.0.98

- updated msaDocModels

# 0.0.97

- add field embedding_attachments to separate attachments

## 0.0.96

- add patterns for models TextExtractionFormatsInput
- separate DTO model for three TextExtractionFormatsStrDTO, TextExtractionFormatsListDTO, TextExtractionFormatsDictDTO

## 0.0.95

- fix model queue in TextExtractionFormatsDTO

# 0.0.94

- fix EntityExtractorInput, EntityExtractorDocumentInput models

# 0.0.93

- update input models for Formats and Template
- add new pub/sub topics

# 0.0.91

- update msaDocModels

# 0.0.90

- update msaDocModels

# 0.0.89

- update msaDocModels

# 0.0.88

- use loguru if dapr is not available

# 0.0.87

- removed self-polling of the healtcheck

# 0.0.86

- fix health tread

# 0.0.85

- fix health tread

# 0.0.84

- fix healthcheck response
- fix ProcessStatus model

# 0.0.83

- fix health tread
- change initial status for document
- added RemoveFolderInputModel and ClearOutDocumentInputModel models
- added AvailabilityML for ML services

# 0.0.82

- change models for filter documents by status

# 0.0.81

- load variables from env

# 0.0.80

- fix init sentry

# 0.0.79

- add models for working with document statuses
- add sentry to project

# 0.0.78

- add model to working with document for Summary/Phrases

# 0.0.77

- add output_file_paths field to document
- fix model to working with documents

# 0.0.76

- add models to working with full document/pages/paragraphs/sentences

# 0.0.75

- change pubsub topic

# 0.0.74

- fix scheduler
- add some fields for document

# 0.0.73

- fix healthcheck
- add logger to redis topic

# 0.0.72

- fix model TextExtractionDefaultsDTO

# 0.0.71

- don't update config when local config have only new version

# 0.0.70

- add name of service and version to /sysinfo and /sysgpuinfo
- add profiler endpoint without middleware
- add function for loading config

# 0.0.69

- fix information_extraction_answer key

# 0.0.68

- Change keys from answers/questions to result

## 0.0.67

- Add models for information extraction

## 0.0.66

- Remove taxonomy stuff

## 0.0.65

- Remove fields active and inherited for learnsets/testsets/models
- Add models to get list of learnsets/testsets/models

## 0.0.64

- Add profiler endpoint

## 0.0.63

- Add models to extended endpoints in summary

## 0.0.62

- Add models to extract phrases from text

## 0.0.61

- Add models for extract Keywords
- Fix empty name of the largest CPU process

## 0.0.60

- Add models for Phrases mining

## 0.0.59

- Update OpenAPI model
- Change model of word bag

## 0.0.58

- Update version of setuptools

## 0.0.57

- Add possible to save learnset object and testset object.

## 0.0.56

- remove language from extraction NLP

## 0.0.55

- change model for NotaryDTO, when notary are not found

## 0.0.54

- change model for NotaryDTO, when notary are not found

## 0.0.53

- add input and output  models for Notary

## 0.0.52

- fix model for result NER

## 0.0.51

- fix model for result Defaults

## 0.0.50

- add models for result of NLP, NER services
- add function to get all sentences per page

## 0.0.49

- fix fields for TextExtractionDocumentNLPInput

## 0.0.48

- add id to ExtractionDefaultResult, RecognizerDefaultResult
- add defaults for TextExtractionDefaults model

## 0.0.47

- change structure for DBBaseDocumentInput
- add models for TextExtractionDefaults, TextExtractionNLP

## 0.0.46

- update dapr version to 1.9.0

## 0.0.45

- update version msaDocModels, change  AutoMLStatus model

## 0.0.44

- update version msaDocModels, fix typo in webhook url

## 0.0.43

- update version msaDocModels, add webhook url and constant to train model

## 0.0.42

- update version msaDocModels, add language for DataCleanAIInput

## 0.0.41

- update version msaDocModels, for default Language and fix send config to pubsub

## 0.0.40

- update version msaDocModels, for TextKeywords

## 0.0.39

- update version msaDocModels

## 0.0.38

- update version msaDocModels

## 0.0.37

- update version msaDocModels

## 0.0.36

- update version msaDocModels

## 0.0.35

- pinned package versions

## 0.0.34

- update requirements

## 0.0.32

- fix sending config
## 0.0.31

- remove require service name in logger_info

## 0.0.30

- add service title in send config

## 0.0.29

- update requirements

## 0.0.28

- update requirements

## 0.0.26

- Remove fs
- Add sql_db_url to config

## 0.0.25

- added service name for info_pub logger

## 0.0.24

- Fix constants

## 0.0.23

- The configuration logic has been implemented. When the service starts, it sends its config to the another service and waits for a new config from it, if there is none, it starts with the default

## 0.0.22

- Update requirements

## 0.0.21

- Remove system endpoints

## 0.0.20

- Added license_info, contact, terms_of_service, openapi_tags for MSAApp

## 0.0.18

- install the latest version of MSA packages

## 0.0.17

- update version of msaDocModels

## 0.0.16

- update version of msaDocModels

## 0.0.15

- remove dependencies from libraries to working with db

## 0.0.14

- update version of msaDocModels, remove libraries to working with db

## 0.0.13

- update version of msaDocModels, add  models

## 0.0.12

-  off schedulers in base config

## 0.0.11

- update version of msaDocModels

## 0.0.10

- add pytest,add dapr port

## 0.0.9

- Add pub_sub to logger (info_pub), add function for convert different types to string

## 0.0.8

- Add pytest, add dapr port

## 0.0.7

- Add upload config from file, add url for json db

## 0.0.6

- update msaDocModels version, remove msaSDK package, add sysrouters
## 0.0.5

- Update msaDocModels version

## 0.0.3

- Add packages and update msaDocModels

## 0.0.2

- Add packages

## 0.0.1

- This is the first public release of msaBase, former releases are all stages of development and internal releases.

