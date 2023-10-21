# LaserOMS

Lightweight python based local order/business management system with Etsy integration

## Features:

- Order tracking and management
- Task management
- Expense tracking
- Wordpress plugin Easy Cart integration
- Etsy integration (Via Remote Server)
- Amazon integration (WIP)
- Product spreadsheet connection
- Packing slip generation
- Customization and flexibility
- Windows and Linux support

## Installation:

Place entire main code into a folder.\
Most of the additional file paths can be change in settings, but it is important to note the database json file is always stored in the parent folder of the code.\
To finish installation, run the file

    installer.py

Answer any prompts that appear. After the installer finishes, run the file

    Main_Gui.py

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
When creating a new expense, the user enters a name of the expense, the amount, and a description. The total price of the expense is calculated by multiplying the unit price by the quantity to avoid user calculation errors. The date of the expense can be changed by entering a different date. The date defaults to the current date. For the purposes of taxes, and deduction reporting, the user can attach an image of a receipt or confirmation of purchase to each expense. For multiple images, separate expenses should be created. Images attached are copied to a separate and user definable folder. Original images may be deleted after and expense is created.

Etsy sends shipping labels confirmation receipts as emails. These can be imported into the system by selecting the import shipping label expense button in Financial Statistics. The user downloads the email as a pdf, and selects this in the import window. The system will automatically extract the shipping number, and the total price from the pdf. The user can then confirm the expense and commit it to the database.

### Settings:

The settings page can be accessed by selecting the settings button in the main window.\
The user will be prompted to enter the password to access the settings page. The default password is 'admin' but it is recommended the user change this.\
The settings page contains a large list of settings. Double clicking a setting will allow the user to change the value of the setting. A pop-up will ask the user to: select yes or no, enter text, select a file, select a folder, or pick a color.
The password can be changed by selecting the password setting. The user must enter the same password twice to confirm the change. The password settings will display an obfuscated version of the password for security.\

### Etsy Request Server:

See more about the server [here.](/Etsy_Request_Server/README.md)\
The Etsy request server is the address of the running request server. This is used to connect to the Etsy API. The default is 'leboeuflasing.ddns.net'. And is hosted by me. You may run your own server if needed. The system requires a Shop ID for the Etsy shop. Find it by using this guide: https://support.sellbrite.com/en/articles/4793390-locating-your-sales-channel-ids

Rate limiting is in effect on the public server. 10 connections can be made per day. This is in an attempt to prevent abuse and stop brute force attacks. If you need more connections, consider running your own server.

#### Optimization

The Request server and etsy ingest attempt to limit ingest time by reducing the number of orders ingested, as a shop with 100 orders or more may take significant time to synchronize. By default only existing open orders and new orders and downloaded by Laser OMS. The idea is that complected orders are generally unchanged. However there is a temporary override in the settings menu if there are inconsistencies.

### Statistics:

The statistics page can be accessed by selecting the statistics button in the main window. This will open a new window with the statistics of finances broken down by year and month. A list of expenses can be show, and searched through by name or date. Double clicking on each expense will open a new window with the details of the expense. Selecting the open image, will open the default image viewer on the system with the expense attached image.\

## Projects:

- Amazon integration
- Shipping integration
- Customizable product data synchronization
- Multiple Instance support or database locking
- Make each window look more modern

## Changes:

Version 1.2.8

- Fixed Etsy Ingest Dead Token Bug
  Etsy Oauth Tokens permanently expire after 90 days of no use. Upon communication with request server, LaserOMS and the Request Server coordinate removal of dead tokens. (There is currently no other way to remove tokens manually as a security measure.)
- Fixed Etsy Ingest Oauth Token Generation Bug
  The process of generating an Oauth token requires a URI from the user. Tkinter inputs do not function from a thread. The process of generating a token has been moved to the main thread. When tokens are setup successfully, a deamon thread will be started to handle the ingest.

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
