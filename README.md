# Item catalog
## Project description

The Item Catalog presents the user with a web application that allows them to view different types of sports, and the items that are associated with each sport. Additionally each item contains a description explaining what the item is used for. If a user is logged in to the website, the user can also create, edit, and delete items to and from the database.

### Requirements
1. Vagrant -  (https://github.com/udacity/fullstack-nanodegree-vm/blob/master/vagrant/Vagrantfile)
2. VirtualBox - (https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
3. Python

### Steps to Run
1. Initialize the virtual machine
```
vagrant up
vagrant ssh
```
2. Navigate to the project folder 'catalog' inside the vagrant directory
```
cd /vagrant/catalog
```
2. Create script to create database file
```
python database_setup.py
```
2. Execute catalog filler script in order to populate database with sports categories
```
python catalog_filler.py
```
3. Execute python script
```
python catalog.py
```
1. In the browser of your choice, navigate to http://localhost:5000

2. Begin adding items and their descriptions to the database.
