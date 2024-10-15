# JimmsScraper Version 2.3 - Scrape products from jimms.fi
>***Ver. 2.3***

# License
This program uses the GNU General Public License (GPL) version 3
Chrome and Chromedriver belong to their respective owners. Read "/chrome-win64/ABOUT" and "/chromedriver-win64/LICENSE.chromedriver" for more license information.

# Created by
Created by Benjamin Willför/TerminalSwagDisorder & KoneAvustajat <br>
Co-created by Sami Wazni & Alexander Willför <br>
In collaboration with Tekniikkatie

# Brief explanation
This program is created for the purpose of scraping computer parts from jimms.fi into an SQLite3 database. <br>
A full run of the version 2 program takes around 45 minutes, which is quite faster from version 1, which took around 1 hour and 15 minutes on average to run. This of course depends on how much data is processed. <br>
The program might bug out in case of a low download speed (under 500kb/s), so please only run the code if the speedtest of the program has not warned of low speed.

# Installation & How to use
Please run setup.py to install dependencies, or check requirements.txt in case you wish to manually install them. <br>

Current iteration uses Selenium, which uses chromedriver. Version 2.2 and above of JimmsScraper uses chrome for testing, which means that you do not need to have your own chrome installation nor the same chrome version as chromedriver. In case you want to update to a newer version of chrome and chromedriver, download your version from here: https://googlechromelabs.github.io/chrome-for-testing/ and replace the chromedriver-win64 and chrome-win64 folders with the new versions folders. <br>

You must download the chrome-win64 program yourself from the above link. Either download the same version as the current chromedriver or replace both chromedriver-win64 and chrome-win64 with the same version. <br>

The program is run by running the JimmsScraper.py file. <br>

Please note that due to "case" being a reserved word in SQLite 3, we use the word "chassis" instead. <br>

An up to date (15.10.2024) database is found in the database folder. Current version of program only inserts into database, so if you need an updated version, you must delete the db file and run the program.

# Bug reports and contact
To report any bugs, or for any other contact please email me at: benniebest1 (at) gmail (dot) com. 
In the subject include the program or file name, the reason for contact (eg. Bug report) and your git username. In the content itself provide either a detailed report, and/or screenshots with explanations. <br>