BEFORE YOU DO ANYTHING, GO TO link_pitchers_to_existing_no_hitters.py and find 'database: ' and specify the name of the database to what you want to inser this into

cd to this folder, launch mariadb, then run these in order:
\. ./missingdata.sql
\. ./createtables.sql
\. ./no_hitters_inserts_v2.sql

Then you can run the py file to do the rest of the inserts:
quit mariadb
python link_pitchers_to_existing_no_hitters.py 

