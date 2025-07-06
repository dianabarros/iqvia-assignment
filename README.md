## Patient-Allergy Pipeline

### How to run
Make sure you have docker and python3 installed. This code was created with Python 3.12.3. Run:
```make up```

### How to test
Run:
```make test```

### Solution details and remarks

#### Pipeline

![pipeline](https://raw.githubusercontent.com/dianabarros/iqvia-assignment/main/pipeline.png)

This solution is a simplification of a pipeline, where we have a reader entity, here being a python script reader.py that reads the provided NDJSON files and insert its content in a Postgres database for raw data. This reader entity should be a representation of a tool that would be constantly receiving messages and uploading them to the database. As we are persisting it in a RDB, we have an `ack` column that will assure the row is not read by the handler more than once.

We have a handler entity, here represented as a python script, that checks the raw data RDS, checks the unacked rows, processes them and input them to a refined Postgres database as the model below

![models](https://raw.githubusercontent.com/dianabarros/iqvia-assignment/main/models.png)

Due to the time for modeling and developing, there are certainly improvements to be done:
- tests should be more assertive and there should be more tests
- error handling should be more purposeful and informative
- code could be more modular to help debugging in the future and reusable
- some variables could be parametrized so the processing could be adjusted in a easier way
- the modeling was done considering the sample received, it would be needed more knowledge about the source data and how it would be used for a better modelling