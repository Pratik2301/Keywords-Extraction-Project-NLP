Backend Code is written in nodejs folder.
Frontend code is written in vuejs folder.

1. run the backend server : node server.js
2. run the frontend code : npm run serve

**Note - The server should be run first.**

**nodejs/controllers/**
`movie.controller.js` contains code to create and save the movie information
Database creation is done in `movie.model.js` file
All the routes have been declared in `movie.routes.js`

Mongodb Atlas username and Password should be edited- "pratik:pratikmc" -> "username:password"

In `server.js`, ExpressJs is used to help to manage Routes and database is configured and connected


**vuejs**

The frontend is written in vue.js.
The important file is main.js where all the create, view_all, view_one routes have been defined.
`app.js` - Navbar and its styling is done in app.js

create.vue - contains code to create Input fields
`Edit.vue` - contains code to view individual movies by their ids
`Index.vue` - contains code to view all the movies
-> the view individual movies can be viewed but can't be edited.
