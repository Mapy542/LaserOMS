# LaserOMS

Lightweight python based local order/business management system with Etsy integration

## Features:

- Order tracking and management
- Task management
- Expense tracking
- Wordpress plugin Easy Cart integration
- Etsy integration (Via Remote Server)
- Inventory management
- Product spreadsheet connection
- Packing slip generation
- Product label generation
- Customization and flexibility
- Windows and Linux support

## Installation:

Place entire main branch code into a folder.\
Most of the additional file paths can be change in settings, but it is important to note the database json file is always stored in the parent folder of the code.\
To finish installation, run the file

    installer.py

Answer any prompts that appear. After the installer finishes, run the file

    Main_Gui.py

## Overview:

The LaserOMS is a local order management system that is designed to be lightweight and easy to use. It is all natural python meaning it works cross platform, although Apple MAC is untested.
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
When creating a new expense, the user enters a name of the expense, the amount, and a description. The total price of the expense is calculated by multiplying the unit price by the quantity to avoid user calculation errors. The date of the expense can be changed by entering a different date. The date defaults to the current date. For the purposes of taxes, and deduction reporting, the user can attach an image of a receipt or confirmation of purchase to each expense. For multiple images, separate expenses should be created. Images attached are copied to a separate and user definable folder. Original images may be deleted after and expense is created.

Etsy sends shipping labels confirmation receipts as emails. These can be imported into the system by selecting the import shipping label expense button in Financial Statistics. The user downloads the email as a pdf, and selects this in the import window. The system will automatically extract the shipping number, and the total price from the pdf. The user can then confirm the expense and commit it to the database.

### Settings:

The settings page can be accessed by selecting the settings button in the main window.\
The user will be prompted to enter the password to access the settings page. The default password is 'admin' but it is recommended the user change this.\
The settings page contains a large list of settings. Double clicking a setting will allow the user to change the value of the setting. A pop-up will ask the user to: select yes or no, enter text, select a file, select a folder, or pick a color.
The password can be changed by selecting the password setting. The user must enter the same password twice to confirm the change. The password settings will display an obfuscated version of the password for security.

### Inventory Management:

The inventory management page can be accessed by selecting the inventory button in the main window.\
The inventory management page allows the user to track inventory for consignment stores or other systems. The user can add new items to the inventory, and edit existing items. The user can also delete items from the inventory.\
During the creation of a new order, the user can select to affect inventory. This will remove the items from the inventory.

### Etsy Request Server:

See more about the server [here.](/Etsy_Request_Server/README.md)\
The Etsy request server is the address of the running request server. This is used to connect to the Etsy API. The default is 'leboeuflasing.ddns.net'. And is hosted by me. You may run your own server if needed. The system requires a Shop ID for the Etsy shop. Find it by using this guide: https://support.sellbrite.com/en/articles/4793390-locating-your-sales-channel-ids

Rate limiting is in effect on the public server. 10 connections can be made per day. This is in an attempt to prevent abuse and stop brute force attacks. If you need more connections, consider running your own server.

#### Optimization (WIP, disabled)

The Request server and etsy ingest attempt to limit ingest time by reducing the number of orders ingested, as a shop with 100 orders or more may take significant time to synchronize. By default only existing open orders and new orders and downloaded by Laser OMS. The idea is that complected orders are generally unchanged. However there is a temporary override in the settings menu if there are inconsistencies.

### Statistics:

The statistics page can be accessed by selecting the statistics button in the main window. This will open a new window with the statistics of finances broken down by year and month. A list of expenses can be show, and searched through by name or date. Double clicking on each expense will open a new window with the details of the expense. Selecting the open image, will open the default image viewer on the system with the expense attached image.

### Product View:

The product view page can be accessed by selecting the see all products button in the main window. This will open a new window with a list of all products in the system. There is a selection option to generate product labels. The user can select generate product labels, and select the products they want to generate labels for. The software will generate and open images of the labels in the default image viewer. These can be printed or saved as needed.

## Projects:

- Amazon integration
- Shipping integration (USPS API or ShipStation API)
- Customizable product data synchronization
- Make each window look more modern
- Add more inventory management features
- Add inventory statistics and reports
- Add inventory stock alerts to tasks.

## Changes:

Version 1.3.4

- Fixed Inventory Management Selection Bug
- Fixed Order Details Window Bug, Incorrectly Saving Modified Orders
- Added Delete Image on save for Expenses
- Added Notes to Orders
- Added Notes to Packing Slips
- Added Customizable Packing Slip Company Information
- Added Product Label Generator
- Added Amazon Expense Ingest for Order invoices.
- Added database lock to prevent multiple instances of the software from concurrently mutating data.

Version 1.3.3

- Fixed USPS Shipping Label Expense Import Bug
- Added Expense type selection from main window
- Added Update Check Frequency to settings. Github API rate limits are 60 requests per hour.
- Fixed bug with inventory management page item selection.
- Fixed bug with details window incorrectly saving modified orders.

Version 1.3.2

- Added inventory window item sorting and column alignment.

Version 1.3.1

- Order Details Window utilizes item product snapshots.
- Added Inventory Management for Consignment Stores tracking.
- Added ability for new orders to affect inventory.
- Fixed bug within new/edit order: packing slip generation not working on export.

Version 1.2.9

- Fixed Etsy Request Server Memory Cache Loss Bug
- Fixed Etsy Request Fast Auth Bug
- Added Local Etsy Token Deletion Option

Version 1.2.8

- Fixed Etsy Oauth Token Creation Bug
- Fixed Etsy Ingest Bug
- Added ability to delete Etsy token

- Etsy Request Server now weekly refreshes tokens to prevent token expiration

Version 1.2.7

- Added USPS Shipping Label Expense Import
- Fixed Details Window Changing Pricing Option Bug
- Reformatted with 110 character line limit

Version 1.2.6

- Fixed Decimal To String Bug
- Fixed Decimal Implementation Bug

Version 1.2.5

- Fixed Addition Arithmetic Bug
- Added Full Negative Decimal Support
- Added Delete Expense Button
- Other Bug Fixes

Version 1.2.4

- Fixed Etsy Ingest
- Fixed Etsy Shipping Expense Import bug
- Handle New Order Autofill Exceptions
- Added float-less arithmetic for monetary calculations
- Other small bug fixes

Version 1.2.3

- Added Etsy Shipping Label Expense Import

Version 1.2.2

- Optimized Etsy request. (Force update all in settings.)
- Added double click to view orders
- Upgraded settings management
- Changed welcome messages
- Improved EasyCart and Etsy View Order Window
- Added Database Trim tool.
- Other small bug fixes

Version 1.2.1

- Fixed Export Expense to handle multiple image file types
- Fixed other small bugs

Version 1.2.0

- Added Etsy integration
- Added ability to view orders from Etsy in the details page

Version 1.1.3

- Expense statistics upgrades
- - Added ability to view expense details and attach expense images
- Added expense report generation
- Finance statistics upgrades
- Installer bug fixes
- Fixed Packing slip generation printing method

Version 1.1.2

- Finance statistics and packing slip generation bug fixes

Version 1.1.1

- Quality of life features
- - Settings stay in consistent order
- - Automatic updates of software
- - View all details of tasks and orders
- Bug fixes
- - Fixed major bug with default path selection in windows

Version 1.1.0

- TinyDB based data management
- Added the Easy Cart Wordpress plugin integration
- Added settings page and password protection
- Added additional information in task and expense pages
- Added customizable order, task, and expense dates

Version 1.0.0

- Original release with object oriented code.
