# Data Dictionary: Sports Outcome Predictor

A data dictionary is a document that describes the structure, data types, and relationships of the data used in an application. This data dictionary provides an overview of the tables, fields, and relationships for the Sports Outcome Predictor application. Placeholder names are used where specific field names are not yet determined.

## Table 1: sports_data

This table contains general sports data for football, basketball, horse racing, baseball, and golf.

| Field Name     | Data Type  | Description                                                |
| -------------- | ---------- | ---------------------------------------------------------- |
| id             | Integer    | Unique identifier for each record                          |
| sport          | String     | The sport type (e.g., football, basketball, etc.)         |
| event_date     | Date       | Date of the event                                          |
| event_location | String     | Location of the event                                      |
| team_1         | String     | Name of the first team or participant                      |
| team_2         | String     | Name of the second team or participant (if applicable)     |
| result         | String     | Result of the event (e.g., winner, score, finishing time) |

## Table 2: ancillary_data

This table contains ancillary data related to the sports events, such as weather conditions, player statistics, or other relevant information.

| Field Name       | Data Type  | Description                                                  |
| ---------------- | ---------- | ------------------------------------------------------------ |
| id               | Integer    | Unique identifier for each record                            |
| sports_data_id   | Integer    | Foreign key referencing the `id` field in the `sports_data` table |
| data_type        | String     | Type of ancillary data (e.g., weather, player statistics)   |
| data_value       | String     | Value of the ancillary data                                  |

## Table 3: model_data

This table contains information about the machine learning models used for prediction.

| Field Name         | Data Type  | Description                                                  |
| ------------------ | ---------- | ------------------------------------------------------------ |
| id                 | Integer    | Unique identifier for each model                             |
| sport              | String     | The sport type (e.g., football, basketball, etc.)           |
| model_type         | String     | Type of machine learning model (e.g., neural network, forest regression) |
| model_parameters   | JSON       | Model parameters in JSON format                              |
| training_data_size | Integer    | Number of records used for training                          |
| last_trained       | Date       | Date when the model was last trained                         |

## Table 4: simulation_results

This table contains the results of the simulations run using the trained predictive models.

| Field Name    | Data Type  | Description                                                  |
| ------------- | ---------- | ------------------------------------------------------------ |
| id            | Integer    | Unique identifier for each simulation result                 |
| model_id      | Integer    | Foreign key referencing the `id` field in the `model_data` table |
| sports_data_id| Integer    | Foreign key referencing the `id` field in the `sports_data` table |
| predicted_result | String   | Predicted outcome of the event based on the simulation       |
| actual_result | String     | Actual outcome of the event                                  |

These tables, along with their relationships, form the foundation for storing and managing data in the Sports Outcome Predictor application. The data dictionary should be updated as needed to reflect any changes to the data structure or new data requirements.
