# Ambrosini Ballet

## Table of contents:
- [What is it?](#what-is-it)
- [How did I do it?](#how-did-i-do-it)
- [Why this way?](#why-this-way)
- [Video Demo](#video-demonstration)
- [File disposition](#file-disposition)
- [File description](#file-description)
- [Usage](#usage)

### What is it?
This is my final project for CS50x course. It is a web app that will allow my sister, Maria Clara Ambrosini, to run her ballet academy's payments and manage her students.
The url to access my web application is https://gabriel1607.pythonanywhere.com/

### How did I do it?
I have written it and tested it within a free online web-app-hosting service, **Python Anywhere** (pythonanywhere.com).
The tools which I have used in Python Anywhere are **Flask**, **Python**, in my *flask_app.py* file, and **MySQL**, which I linked to my python program through *MySQL connector*. The web pages are built with **HTML** and **CSS**, and besides I also used **Jinja** to build connections between html pages and between the python file and the html pages.
At the start I intended to use AI, which would allow me to then enhance web application details with my skills; however, I did not find one that would satisfy my needs, so AI did not have an impact on this project.

### Why this way?
Before I found Python Anywhere, I was searching some free web-app hosting-service outside of CS50, so as to try to take off my training wheels. Python Anywhere provided me with a python-flask backend option outside of CS50, which is what I was looking for; besides python-flask backend is a structure I was already familiar with, so these thoughts determined my choice.
With the same mindset, I decided to use Spanish for most of my project, in other words, so as to do something different from CS50.

### Video Demonstration:
Here is a demonstration of the usage of Ambrosini Ballet web application, via a YouTube video:
https://www.youtube.com/watch?v=3mj9XCQ4IpQ

### File disposition
The structure of my project starts with the *mysite* folder, within which I have subsequent files and folders:
- [*flask_app.py*](#flask_apppy), the python backend
- [*helpers.py*](#helperspy), another python file which defines a route decorator function for the main python file
-*requirements.txt*, states which libraries need to be installed for the web application
- *static* folder, within which there are:
	- [*estilo.css*](#estilocss), *estilo* is the spanish for "style."
	- *Ambrosini_Ballet.jpg*, the image for the homepage
- *templates* folder, within which there are:
	+ [*disposicion.html*](#disposicionhtml), the equivalent of a *layout.html*
	+ [*index.html*](#indexhtml), homepage with an image
	+ [*solicitud.html*](#solicitudhtml), for user registration requests
	+ [*login.html*](#loginhtml), for log in
	+ [*solicitudes.html*](#solicitudeshtml), for the administrator to see registration requests
	+ [*usuarios.html*](#usuarioshtml),  for the administrator to see the users
	+ [*cclave.html*](#cclavehtml), for the administrator to change users' passwords
	+ [*pagos.html*](#pagoshtml), for the administrator to see users' registered payments
	+ [*pago.html*](#pagohtml), for a user to register a payment

### File description
Now I will delve deeper into each file:

##### *flask_app.py*
This is the python backend which controls the flow of information between my MySQL database and my web page templates.
To start, I import a lot of libraries to serve my purposes:
- Flask and related imports, which allow me to connect my backend to my frontend
- Flask session, to manage logins
- Werkzeug password encription functionality, to establish a security measure for my web app
- Route decorator functionality from functools
- The login required route decorator from *helpers.py*
- Finally, MySQL connector to link my Python backend to my MySQL database.

After this, there a few necessary lines for the app to run properly. Then, I link my database by calling MySQL connector and stating the host, user, password, and database.
Thereafter I define a new route decorator which will restrict routes to a certain type of user, "administracion", or, in other words, to "admin" users.

Below this comes the definition of the default route ("/"), which simply renders *index.html* if there is no login, or, if there is, renders it and states the variable *tipo*, which allows the display of the navigation menu and prevents certain elements of the non-login version from being rendered.

Next, the "/login" route is defined, which, if accessed via GET method, will render *login.html* or, if accessed via POST method, will validate username and password from user input to start a session. If username or password are invalid, *login.html* is rendered with an error message. Passwords are checked via *check_password_hash* function, since passwords are encripted within the database. If login is succesful, the user is redirected to the default route ("/").

Next is the "/logout" route, which simply clears the session.

The following route is "/cclave", which changes user's passwords in the MySQL database ("cclave" stands for "cambiar clave", Spanish for "change password") and can only be accessed via post in order to help keep user information private and secure. Following the same purpose, it has the *@admin* route decorator, which means that only administrator users can access this route, besides the *@login_required* decorator.
I use the *generate_password_hash* function from werkzeug security to keep passwords encripted and secure.

Then comes the "/solicitud" route, which, if accessed via GET, renders *solicitud.html* and specifies the *tipo* variable, which will modify certain details in its rendering. On the other hand, if it is accessed via POST, will insert into the database a user registration request, of type "profesora" or "alumna."

Next in the file there is the "/pago" route, which, if accessed via GET, renders *pago.html*, from which user input will be collected and from which this route will be accessed via POST, which will insert into the database a payment ("pago" is Spanish for "payment"). It restricted to logged-in users, via the *@login_required* decorator.

Now comes the "/borrar" route, which can only be accessed via POST, and serves the purpose of erasing data from the database, either a user registration request, an user, or a payment. It is restricted to logged-in users of the type administrator, via both of the already mentioned route decorators.

After a couple of lines the "/aceptar" route is found, which can only be accessed via POST and serves to modify entries in the database: to set payments ("pagos") as confirmed ("confirmado") and to accept user requests. The first lines of the route confirm payments, then come many lines to register a user and to forget the user request once the user is registered. The "/solicitudes" route is called at the end. It has *@login_required* and *@admin* as decorators.

Next is the "/solicitudes" route, which loads all user registration requests and renders *solicitudes.html*. It has *@login_required* and *@admin* as decorators.

Next comes the "/usuarios" route, which only accepts GET method, loads the information from all the users but the logged-in one, and renders it in *usuarios.html*. It has *@login_required* and *@admin* as decorators.

Next is the "/pagos" route, which loads all payments and corresponding usernames from the database and renders them in *pagos.html*. It has *@login_required* and *@admin* as decorators.

The last part of *flask_app.py* is the "/mispagos" route which loads the logged-in user's payments and renders them in *pagos.html*. It has the *@login_required* decorator.

##### *helpers.py*
The @login_required decorator is defined here. If any of the routes within *flask_app.py* that have this decorator are called while there is no log-in, users will be redirected to the default route ("/").

##### *estilo.css*
This css style sheet defines certain classes to make the webpages from the web app look better:
- The main header in *disposicion.html*
- Many buttons with "btn1" class
- And the navigation bar

##### *disposicion.html*
This is the layout page or template for the rest of the html files. I called it "disposicion" because "disposición" is the Spanish for "layout."
At first, it defines certain size characteristics and links the wep page to certain style sheets.
It has a block called "head" at the head of the html for other html files to add content there.
It includes a h1 element to be the header of all of the pages of this web app, with a link to the default route ("/").
It also has a block called "bar" for other html files to add options to the navigation bar. Finally, it has the "main" block to add all of the bulk of the content of other htmls there.
It includes the a navigation bar with clickable links that will open different routes which will render other html files. Some of these options will be rendered or not depending on the type of logged-in user.
- *Solicitudes* (opens "/solicitudes")
- *Usuarios* (opens "/usuarios")
- *Pagos* (opens "/pagos")
- *Revisar pagos* (opens "/mispagos")
- *Ingresar pago* (opens "/pago")
- *Cerrar sesión* (opens "/logout")

##### *index.html*
This html file, as the rest will, extends *disposicion.html*, and specifically within its "main" block.
If there is no user log-in, there is a form with a button and a select element, which opens "/solicitud" via GET. The no-log-in user can choose wether he wants to do a user request as a teacher ("profesora") or as a student ("alumna").

Regardless of log-in, *Ambrosini_Ballet.jpg* is rendered.

##### *solicitud.html*
This html file displays some elements differently depending on what type of request the user made in *index.html*, with the help of Jinja logic. It has many fields within a form that calls "/solicitud" via POST, loading user input into the python program.

##### *login.html*
It has a simple form to send user input to the python file via POST within the "/login" route. It also has an optional alert message at the beggining if the variable "aviso" equals "clave."

##### *solicitudes.html*
It will display all the user requests in a list-like table. Jinja allows for a single structure to be repeated over and over again to place each user request into the table. Each element has two buttons, which call "/borrar" and "/aceptar" respectively.
If no user requests are loaded, an alternate message will be displayed, thanks to Jinja logic.

##### *usuarios.html*
Very similarly to *solicitudes.html*, it will display all the users, except the logged-in one, in a list-like table. It uses the same Jinja technique for iteration and each element has two buttons which will call "/borrar" and "/cclave" respectively.
If no users are loaded, an alternate message will be displayed.

##### *cclave.html*
It has a simple form to send user input to the "/cclave" route via POST, with an optional error message which is displayed if the "alerta" variable is defined.

##### *pagos.html*
Very similarly to both *solicitudes.html* and *usuarios.html*, it displays all the payments, confirmed or not, in a list-like table. It uses the same Jinja technique for iteration and each element has two buttons which call "/aceptar" and "/borrar" respectively.
If no payments are loaded, an error message is displayed instead.

##### *pago.html*
It has a simple form to send user input to the "/pago" route via POST, with a couple of optional error messages to be displayed, plus a success message if user input is successfuly entered into the database.

### Usage
Now a brief of explanation of how each type of user navigates through the web application.

##### Non logged-in user
This user starts at the *index.html* page, from which he can click either "solicitar registro" (in English "ask for registration") or "iniciar sesión" (in English "Log in"). The first button takes him to *solicitud.html*, from which the a user registration request can be recorded in the database. The "iniciar sesión" button takes the user to *login.html*, from which the user can validate his credentials and be redirected to *index.html*. At this point, the user type changes. This is what's coming next.

##### "*Administracion*" user
Starting from the *index.html* again, only this time logged in as "administracion," the user may select several options from the navigation bar, many of which are exclusive to this type of user. At any point in any of the htmls, the user may click the "Ambrosini Ballet" header to go back to *index.html*. Here are the navigation bar options:
- Solicitudes
	+ Loads *solicitudes.html*, where user registration requests are displayed in a table. Each element has the "aceptar" and "borrar" buttons, to either transform the request into a registered user or to erase that request. Accepting the user registration request, which creates a new user, also erases the request from the database, by the way. Clicking these buttons will reload the html.
- Usuarios
	+ Similarly to "solicitudes", this will load *usuarios.html*, where users are displayed in a table. You can click buttons "borrar" or "cambiar su clave" for each user, which will respectively erase the user or send you to *cclave.html* where you can change the selected user's password. Both of these options (erasing or changing password in the other html) reload *usuarios.html*.
- Pagos
	+ Loads *pagos.html*. There the user may click on the "confirmar" or "borrar" buttons that are on each element in the payments list-like table, to either change a payment to "confirmado" or to erase a payment from the database. On clicking these buttons, the html is reloaded. The other options from the navigation bar are still there, clickable.
- Cerrar sesión
	+ Logs out and reloads *index.html*.

##### "*Profesora*" and "*Alumna*" users
Starting from the *index.html* again, only this time logged in as either "profesora" or "alumna", the user may select three options from the navigation bar:
- Ingresar pago
	+ Loads *pago.html*, from where you can register an uncofirmed (Spanish "sin confirmar") payment. Registering it succesfully will reload *pago.html* with a success message.
- Revisar pagos
	+ Loads *pagos.html*, where a table of all of the logged-in user's payments are displayed, no buttons included, as they were in other htmls.
- Cerrar sesión
	+ Logs out and reloads *index.html*.

P.D.: I confess I did use AI to generate in two seconds the title page html for my video, not part of the project itself.
