# LaserOMS
Lightweight python based local order/buisness management system with Etsy integration

Basis:
This system is intended to be run on multiple linux computers and all files are accessable via NAS device in a samba share.

Features:

    Order storage, loging, shipping, packing slip generating, and API pulling
    Expence tracking
    Finance staistics
    Task management and schedule via crontab system

Install and Run:

    Create a folder to contain all code and data for Laser OMS. 
    Then create a folder within that folder. It will ONLY HOLD THE CODE. (Everything in this repo)

    Run Installer.py to get all required packages and create all storage folders.

    If using Etsy Api, enter oauth tolkens, api key, and shop keys to access necesary API data in the then created oauth.txt.
    If getting item pricing from a google sheet, include the public link in Pricing_List_Link.txt

    Run Main_Gui.py to start the program on any computer

Things to DO:

    Employee wages tracking 
    Scaleable items for order