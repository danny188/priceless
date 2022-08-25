# Priceless App

Priceless is a full-stack web application that aims to make shopping easier. By creating an account, users can add their favorite products for price tracking, and receive email notifications when those products go on sale.

![Product list screenshot](https://pricelessapp.herokuapp.com/static/img/product_list_screenshot.PNG)

# Main Features

## Receive emails when products go on sale
![Sample email notification](https://github.com/danny188/priceless/blob/main/static/img/product_sale_email_screenshot.PNG?raw=true)

## On-demand 1-click price updates
![Button to update all products](https://github.com/danny188/priceless/blob/main/static/img/refresh_products.gif?raw=true)


## Easy cut and paste product url to add a product
![screenshot of add product page](https://github.com/danny188/priceless/blob/main/static/img/add_product_screenshot.PNG?raw=true)

## Control the frequency and day of email notifications
![screenshot of user settings](https://github.com/danny188/priceless/blob/main/static/img/settings_screenshot.png?raw=true)

# Other Features
- Full user management system
- Live progress bar
- Interactive frontend
- Automatic scheduled price updates and email notifications
- Concurrent price updates
- Interactive product dashboard with filtering and sorting
- Price update frequency limiting

# Built With
- Backend: Python/Django
- Frontend: JavaScript and Django templates
- Celery
- PostgreSQL
- Bulma

# Running the application locally

```sh
$ git clone https://github.com/danny188/priceless.git
$ cd priceless_project
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ venv .
$ $ source <venv>/bin/activate
```
[venv instructions for other platforms](https://docs.python.org/3/library/venv.html)

Then install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```
Note the `(venv)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `venv`.

Once `pip` has finished downloading the dependencies:
```sh
(venv)$ cd project
(venv)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000`.

# Running Tests

To run the tests, `cd` into the directory where `manage.py` is:
```sh
(venv)$ python manage.py test
```