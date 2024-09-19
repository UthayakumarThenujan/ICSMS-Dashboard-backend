Overview
This project is a backend API service built with FastAPI, integrated with MongoDB Atlas and AWS Cognito for user authentication. The API handles data transformations, user notifications via WebSockets, and securely interacts with a MongoDB database. The project is designed to run on port 8002 and is connected to the frontend.

Folder Structure
The project is organized into the following main folders:

1. config/
Description: This folder contains the configuration for connecting to MongoDB Atlas and handling API settings.
Key Files:  db.py: MongoDB Atlas connection setup.

2. models/
Description: Defines the structure of the data formats using FastAPI's BaseModel.
Key Files:  user.py: Contains the data models used across the API.

3. routes/
Description: Contains the main routes that bridge the frontend with the backend.
Key Files:
  route.py: The main routing file handling all primary API requests.
  notify.py: Handles WebSocket notifications to users.
  token_verification.py: Verifies AWS Cognito tokens for user authentication.

4 . schemas/
Description: This folder contains the data transformation functions for handling MongoDB data in the API.
Key Files:
  user.py: Defines functions for transforming data between API and MongoDB.
  
Main File
main.py
Description: The entry point of the API. It runs the FastAPI application and connects to the frontend.

How to Run: The app runs on port 8002.

Run the application:
uvicorn main:app --reload --port 8002