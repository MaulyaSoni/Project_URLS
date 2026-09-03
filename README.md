# PROJECT:-  URL ANALYSER with CLICK Analysis


Here first the user comes to the app
goes to  /register route , here there will be input of three things -> username , email , password .

The password will be stored in hash form with the help of jwt .

Once user registration done , he need to login it for the session using the jwt token 
For that /login route is there , it will be going to take useremail and password , now the plain password will be verify using the PasswordHash and jwt with the hashed_password 

once it verify the bearer auth token will be generated .

For postman that token need to put in the POST->Auth->bearer , and for the Swagger it will be done using the AUTHORIZE button (inbuilt feature of Swagger UI).

Now we have total 14 endpoints

1- General  
GET / 

6 related to the user & its operations 
POST /admin 
POST /user
POST /login 
GET /users/me -> user dependency (should be logged in)
GET /users/all -> admin dependency
DELETE /users/delete/{userid} -> admin dependency

7 related to the url and its operations
POST /url ->user dependency (should be logged in)
GET /url (all URL) -> admin dependency
GET /url/{short_link} 
GET /my/urls ->user dependency 
GET /dashboard  ->admin dependency
GET /url/stats/{url_id} ->current user and admin dependency
DELETE /url/delete/{url_id} ->admin dependency