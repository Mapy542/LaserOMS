<h1># LaserOMS</h1><br>
Lightweight python based local order/buisness management system with Etsy integration<br>
<br>
<h3>Basis:</h3><br>
This system is intended to be run on multiple linux computers and all files are accessable via NAS device in a samba share.<br>
<br>
<h3>Features:</h3><br>
Order storage, loging, shipping, packing slip generating, and API syncronization<br>
Expence tracking and financial reporting<br>
Listing and product management and API syncronixation<br>
Task management<br>
<br>
<h3>Install and Run:</h3><br>
Create a folder to contain all code and data for Laser OMS. <br>
Then create a folder within that folder. It will ONLY HOLD THE CODE. (Everything in this repo)<br>
<br>
Run Installer.py to get all required packages and create all storage folders.<br>
<br>
If using Etsy Api, enter oauth tolkens, api key, and shop keys to access necesary API data in the then created oauth.txt. <br>
If getting item pricing from a google sheet, include the public link in Pricing_List_Link.txt<br>
<br>
Run Main_Gui.py to start the program on any computer<br>
<br>
<h3>Things to DO:</h3>

    Employee wages tracking 
    Scaleable items for order
    more flexible packing slip generation
    amazon integration
    etsy integration
<br>
<br>
<h3> Changes:</h3><br>

Version 1.1.0<br>
    Implimented dynamic pricing and listing management<br>
<br>
Version 1.0.0<br>
    Original release with object oriented code. (was tuple based)<br>
    Task Management included<br>