## Collection and organisation of information about Bulgarian schools

[openSUSE Hack Week 25 project](https://hackweek.opensuse.org/projects/collection-and-organisation-of-information-about-bulgarian-schools)


## Description

To achieve this it will be necessary:

 - Collect/download raw data from various government and non-governmental
   organizations
 - Clean up raw data and organise it in some kind database.
 - Create tool to make queries easy.
 - Or perhaps dump all data into AI and ask questions in natural language.

## Goals

By selecting particular school information like this will be provided:

- School scores on national exams.
- School scores from the external evaluations exams.
- School town, municipality and region.
- Employment rate in a town or municipality.
- Average health of the population in the region.

## Resources

Some of these are available only in bulgarian.

- https://danybon.com/klasazia
- https://nvoresults.com/index.html
- https://ri.mon.bg/active-institutions
- https://www.nsi.bg/nrnm/ekatte/archive

## Results

- Not fully ready.
- Information about _all_ Bulgarian schools with their scores during recent years cleaned and organised into SQL tables
- Information about _all_ Bulgarian villages, cities, municipalities and districts cleaned and organised into SQL tables
- Information about _all_ Bulgarian villages and cities census since beginning of this century  cleaned and organised into SQL tables.
- Information about _all_ Bulgarian municipalities about religion, ethnicity cleaned and organised into SQL tables.
- Data successfully loaded to locally running Ollama with help to Vanna.AI

## TODO
- Seems that tables columns have to have better description to allow LLM to do its magic
- Add comments to column names. This will require switch from SQLite to ... PostgreSQL which supports COMMENTS
- Add more statistical information about municipalities and ....

## HOWTO

- Install [ollama](https://ollama.com) and gpt-oss model
- Install requirements
- Install PostgreSQL database and execute initial configuration
- Fill in database tables
```console
 $ bash build.sh
```
- Start Vanna.AI
```console
 $ ./vannaai.py
```
- Open http://localhost:8000
