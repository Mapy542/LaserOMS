# LaserOMS

Lightweight python based local order/business management system with Etsy integration

## Basis:

This system is designed to track orders, expenses, and inventory.\
It is lightweight and designed to be run on a single computer. (Server Syncing is not yet implemented)\

<h3>Features:</h3><br>
Order storage, loging, shipping, packing slip generating, and API synchronization<br>
Expense tracking and financial reporting<br>
Listing and product management and API synchronization<br>
Task management<br>
<br>
<h3>Install:</h3><br>
Create a folder to contain all code and data for Laser OMS. <br>
Then create a folder within that folder. It will ONLY HOLD THE CODE. (Everything in this repo)<br>
Run Installer.py to get all required packages and create all storage folders.<br>
Fill out any config files that are created.<br>
Run Main_Gui.py to start the program on any computer<br>
<br>
<h3>Usage:</h3><br>
Listings/products for order tracking should be created in a google sheet, or other software that<br>
can edit cvs files. Orders are created via GUI in software, or are pulled from selling channel api.<br>
Tasks are used manage the order process or convey duties to staff. <br>
Expenses are tracked and reported in the GUI.<br>
<br>
Setting up Etsy integration follow: https://pypi.org/project/etsy2/ to get credentials<br>
and then include them in OAuth.txt file.<br>
Last_Order.txt is used to keep track of the last order that was manually created.<br>
It can be adjusted to change manual order numbers. (NOTE IT DOES NOT check for duplicates)<br>
Indicators.txt is used to pull the data out of the cvs file and into the program.<br>
If you have multiple pricing styles, ie charge different amounts based no platform,<br>
include them as an indicator. To be considered not just another data field, put a double asterisk (**)<br>
<h3>Projects:</h3>

    Employee wages tracking
    dynamic items for order
    more flexible packing slip generation
    amazon integration
    etsy integration

<br>
<h3> Changes:</h3><br>

Version 1.1.0<br>
Implemented dynamic pricing and listing management<br>
<br>
Version 1.0.0<br>
Original release with object oriented code. (was tuple based)<br>
Task Management included<br>
