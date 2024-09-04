# WebGame-TreasureAndDungeon

# This project is written and uses the Fast API framework

Basic commands for launching and working with the project:
1) uvicorn main:app --reload  
Launching the project
2) alembic revision --autogenerate -m "Your naming"  
Creating a version for adding to the database

------------------------------------------------
For correct operation, you will need to create a Database based on postgress. To do this, create a database according to the env file settings and update the database using the command:alembic update up

Work address: localhost:8000

Documentation and age for checking the back: localhost:8000/docs
