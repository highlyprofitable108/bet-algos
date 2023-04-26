#!/bin/bash

# Navigate to the Git repository directory
cd https://github.com/mikefusc/mlb-forest-and-neural.git

# Download the Lahman consolidated data file
curl -O http://seanlahman.com/files/database/lahman-csv_2014-02-14.zip
unzip lahman-csv_2014-02-14.zip
mv lahman-csv_2014-02-14/Master.csv lahman_data.csv

# Add the consolidated data file to the Git repository
git add lahman_data.csv

# Commit the changes to the repository
git commit -m "Add Lahman consolidated data file"

# Push the changes to the remote repository
git push
