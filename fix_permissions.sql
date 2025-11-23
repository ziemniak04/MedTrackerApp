ALTER DATABASE medtracker_db OWNER TO "Developer";
GRANT ALL PRIVILEGES ON DATABASE medtracker_db TO "Developer";
\c medtracker_db
GRANT ALL ON SCHEMA public TO "Developer";
