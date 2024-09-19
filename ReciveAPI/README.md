Overview: Recive API
This project is a backend API service built with FastAPI, integrated with MongoDB Atlas and AWS Cognito for user authentication. The API handles data transformations, user notifications via WebSockets, and securely interacts with a MongoDB database. The project is designed to run on port 8002 and is connected to the frontend.

Folder Structure
The project is organized into the following main folders:

1.config/

Description: This folder contains the configuration for connecting to MongoDB Atlas and handling API settings.

Key Files:

   main_dashboard_db.py: MongoDB Atlas connection setup to Main Dashboard DB.
   
   call_db.py: MongoDB Atlas connection setup to Call DB.
   
   email_db.py: MongoDB Atlas connection setup to Email DB.
   
   social_db.py: MongoDB Atlas connection setup to Social DB.
   



2.models/

Description: Defines the structure of the data formats using FastAPI's BaseModel.

Key Files:  model.py: Contains the data models used across the API.

3.routes/

Description: Contains the main routes that bridge the frontend with the backend.

Key Files:

  1. call/
     
       call_preprocess.py: call notification data structures handling.
     
       receive_call.py: call notifications receive from call database .
     
  2. email/

       email_preprocess.py: email notification data structures handling.
     
       receive_email.py: email notifications receive from call database.
     
  3. social/
     
       social_preprocess.py: social notification data structures handling
     
       receive_social.py: social notifications receive from call database
     
     
  initial_process.py: before monitoring watch functions, old datas are check and write in Mongo DB.
  
  route.py: The main routing file handling all primary API requests.
  
  chnaged_data_handel.py: when any changes in data(new data) i will added in MongoDB.
  
  sentiment_tagging.py: in Social media we will calculate the sentiment scores using sub comments and comments , calculate the final score using this function.
  

4.schemas/

Description: This folder contains the data transformation functions for handling MongoDB data in the API.

Key Files:

  schema.py: Defines functions for transforming data between API and MongoDB.
  
  
Main File
main.py
Description: The entry point of the API. It runs the FastAPI application and connects to the frontend.

How to Run: The app runs on port 8001.

Run the application:
uvicorn main:app --reload --port 8001
