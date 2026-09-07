# PROJECT:-  URL ANALYSER with CLICK Analysis


- Here first the user comes to the app
goes to  /register route , here there will be input of three things -> username , email , password .

- The password will be stored in hash form with the help of jwt .

- Once user registration done , he need to login it for the session using the jwt token 
- For that /login route is there , it will be going to take useremail and password , now the plain password will be verify using the PasswordHash and jwt with the hashed_password 

once it verify the bearer auth token will be generated .

- For postman that token need to put in the POST->Auth->bearer , and for the Swagger it will be done using the AUTHORIZE button (inbuilt feature of Swagger UI).

- Now we have total 14 endpoints

- 1- General  
- GET / 

- 7 related to the user & its operations 
- POST /admin 
- POST /user
- POST /login 
- POST /logout 
- GET /users/me -> user dependency (should be logged in)
- GET /users/all -> admin dependency
- DELETE /users/delete/{userid} -> admin dependency

- 7 related to the url and its operations
- POST /url ->user dependency (should be logged in)
- GET /url (all URL) -> admin dependency
- GET /url/{short_link} 
- GET /my/urls ->user dependency 
- GET /dashboard  ->admin dependency
- GET /url/stats/{url_id} ->current user and admin dependency
- DELETE /url/delete/{url_id} ->admin dependency

- Why we do the DB-Session operations in main file whenever we need to modify and update the db 
- The main reasons are:-

- 1) To tackle the 1205 error (transaction lock and wait error) , which generally comes when an db request is pending and a new request comes and want to execute that request . 

- This error and issue comes when updating the task in the get_url_link route , when need to update the stats and need to create a log , this all thing goes into the backgroundtasks and at that time the 1205 comes and i figure out this approach.

- 2) Another reason is precaution for the db session opening but not closing , so using the exception handling we are rollback the db and also closing the db as our work completed , this prevents the error regarding to retrival the data from the database using the ORM Session .

- 3) And this error specifically comes under the upsert operation , when using the on_conflict_do_update operation for changing the data in the URL Stats table , the background tasks takes a long waiting time and the thread goes to sleep and rest operation thread comes in a queue , so in background tasks , not passing the current db session of the route and providing a new session to them , solves this issue and with the exception handling , things works completely.

