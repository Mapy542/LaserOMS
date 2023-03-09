# LaserOMS

Lightweight python based local order/business management system with Etsy integration

## Features:

- Order tracking and management
- Task management
- Expense tracking
- Wordpress plugin Easy Cart integration
- Etsy integration (WIP)
- Amazon integration (WIP)
- Product spreadsheet connection
- Packing slip generation
- Customization and flexibility

## Installation:

Place entire main code into a folder.\
Most of the additional file paths can be change in settings, but it is important to note the database json file is always stored in the parent folder of the code.\
To finish installation, run the file

    installer.py

## Overview:

The LaserOMS is a local order management system that is designed to be lightweight and easy to use.\
The software should not be opened in multiple instances at the same time. Database changes are cached in memory, and multiple instances will create cache inconsistencies (Data Loss).

### Main Window:

The main window is the main hub for the software.
The main window is split into two sections.\
The top section a list of uncompleted orders and tasks, but can be changed to show only orders or all orders in the database.
Selecting an order or task will allow actions to be performed on the selected item.\
The bottom section is a series of buttons that allow the user to do a variety of actions.
The new section allows the user to create a new order, task, or expense.
The modify section allows the user to mark selected orders or tasks as completed, or to edit the selected order or task. Printing packing slips is also available in this section.
The synchronize section allows the user to synchronize the database with the e-commerce apps, or the product list as desired.
Finally, the statistics section allows the user to view statistics about the business. All existing products can be viewed, and financial statistics can be viewed and are broken down by month and year.\
The main window also automatically verifies the application is up to date, and will prompt the user to update if a new version is available. If the system encounters and inconsistency in the settings of the application, it will fix the issue and prompt the user to check the settings for correctness. This may occur after an update. The software will look for a setting to exist, and if it does not, it will create the setting with a default value.

### New Orders:

New orders can be created by selecting the new order button in the main window.\
The new order window has many boxes to fill out. Name and address are used for order identification and shipping on the packing slip. If the system must have product synchronized from a google sheet to pull up product pricing in the new order window.\
Each item added to the order can be selected by typing in the name of the product, or by selecting the product from the drop down menu. The menu is accessed by double clicking the name of the product.\
Upon finishing the order, the user can select to automatically print a packing slip, or to save the order and print the packing slip later.

### New Tasks and Expenses:

New tasks and expenses can be created by selecting the new task or new expense button in the main window.\
When creating a new task, the user gives the task a name, and can fill it out with an additional description. The priority of the task can be selected from 0 to 100. This will affect the order of the tasks being shown on the home page.\
When creating a new expense, the user enters a name of the expense, the amount, and a description. The total price of the expense is calculated by multiplying the unit price by the quantity to avoid user calculation errors. The date of the expense can be changed by entering a different date. The date defaults to the current date.

### Settings:

The settings page can be accessed by selecting the settings button in the main window.\
The user will be prompted to enter the password to access the settings page. The default password is 'admin' but it is recommended the user change this.\
The settings page contains a large list of settings. Double clicking a setting will allow the user to change the value of the setting. A pop-up will ask the user to: select yes or no, enter text, select a file, select a folder, or pick a color.
The password can be changed by selecting the password setting. The user must enter the same password twice to confirm the change. The password settings will display an obfuscated version of the password for security.\

## Projects:

- Etsy integration
- Amazon integration
- Shipping integration
- Customizable product data synchronization
- Multiple Instance support or database locking

## Changes:

Version 1.2.0

- Quality of life features
- - Settings stay in consistent order
- - Automatic updates of software.

Version 1.1.0

- TinyDB based data management
- Added the Easy Cart Wordpress plugin integration
- Added settings page and password protection
- Added additional information in task and expense pages
- Added customizable order, task, and expense dates

Version 1.0.0

- Original release with object oriented code.
