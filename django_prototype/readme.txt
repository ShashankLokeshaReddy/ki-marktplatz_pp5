
Use "python manage.py formatcsv" inside the docker container to prepare the csv for the upload into the admin area. You can and should set df.head(n=) to a value lower than 100000 in order to have sufficient loading times.

In order to upload the csv inside the admin area, you need to click on the machines module and then you can use the import-button at the top of the page.
