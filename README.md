# JimmsScraper Version 2 - Scrape products from jimms.fi

# License
This program uses the GNU General Public License (GPL) version 3

# Created by
Created by Benjamin Willför/TerminalSwagDisorder & KoneAvustajat
Co-created by Sami Wazni & Alexander Willför
In collaboration with Tekniikkatie

# Brief explanation
This program is created for the purpose of scraping computer parts from jimms.fi into an SQLite3 database.
A full run of the program takes around 45 minutes, which is quite faster from version 1, which took around 1 hour and 15 minutes on average to run. 
The program might bug out in case of a low download speed (under 500kb/s), so please only run the code if the speedtest of the program has not warned of low speed.

# Installation & How to use
Please run setup.py to install dependencies, or check requirements.txt in case you wish to manually install them.

Current iteration uses Selenium, which uses chromedriver. Currently using chromedriver for Chrome version 116. In case of other version of chrome, download your version from here: https://googlechromelabs.github.io/chrome-for-testing/ and replace the chromedriver-win64 folder with your versions folder.

The program is run by running the JimmsScraper.py file.

An up to date (15.06.2023) database is found in the database folder. Current version of program only inserts into database, so if you need an updated version, you must delete the db file and run the program.

# Bug reports and contact
To report any bugs, or for any other contact please email me at: benniebest1 (at) gmail (dot) com. 
In the subject include the program or file name, the reason for contact (eg. Bug report) and your git username. In the content itself provide either a detailed report, and/or screenshots with explanations.