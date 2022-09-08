# BoardExplorerLegistar
BoardExplorerLegistar is a Python-based scraper that can be employed to extract data from local government Legistar pages.

## Getting Started

This short guide will inform you how to start using the BoardExplorerLegistar repository to obtain data from Legistar and upload that data to Google Docs.

### Part 1: Getting Data from Legistar

While this repository also allows the user to request data with the Legistar Web API, we will be focusing on data extraction through scraping, as this aspect is more unique to this repository.

1. Clone BoardExplorerLegistar onto your local machine and move noweba.py into your intended working directory. NoWebA.py contains all code related to scraping Legistar pages without the use of the Legistar Web API. It is worth noting that noweba.py requires BeautifulSoup 4, an HTML parsing library, to be installed.
    * To clone this repository, run `git clone https://github.com/LordOfBeans/BoardExplorerLegistar` in the terminal.
    * To Install BeautifulSoup, run `pip install bs4` in the terminal.

2. Create a new Python File in your working directory and type `import noweba` at the top of the file. This will allow you to use the functions and methods in noweba.py.

3. Requests in BoardExplorerLegistar are done primary through the use of dictionaries. The first step in making a request a creating a dictionary that could be representative of one request.
    There are 3 primary types of keys in noweba.py dictionaries:
    1. Text Contains Key <br />
        There are two keys in this category: Text and Title. The use of the Text key filters the legislation such that the provided String will be found in some form in the text of the legislation. Use of the title key will only check the title.
    2. Set Attribute Key <br />
        There are five keys in this category: Type, Status, Index, Controller, and Sponsor. For each of these keys, their value must match one of the values that can be seen in the advanced search view on a Legistar page. As you can see in the below image, there are many options for the Status key on Allegheny County's Legistar page.
        ![Advanced Search on the Allegheny County Legistar Page](AdvancedSearch.png)
    3. Date Key <br />
        The only key in this category is the 'Final Action Date' key. This key's value is itself another dictionary, containing optional Before and After keys, both taking datetime objects as values. The Before key filters all values to have had their final action before that data. The After key does the opposite. If both Before and After Keys are present, the results will be in between those two dates, with the Before key being the later date.
    Now that we know the types of keys, we will set up an example dictionary for Allegheny County. We want to request all Appointments that have been Approved and whose Final Actions occured no more than one year ago.


```python
import noweba
from datetime import datetime, timedelta

today = datetime.now().date()
one_year_ago = today - timedelta(days=365)

county_dict = {
	"Type": "Appointment",
	"Status": "Approved",
	"Final Action Date": {
		"After": one_year_ago
	}
}
```

4. Create a NoWebA object with the appropriate client name. After the object has made some requests and acquired some essential data, you will be able to use it to make your own requests. Building on top of the previous example, we can use the client name 'alleghenycounty' to create a NoWebA object for Allegheny County. The client name is taken from the Legistar page URL, which is `alleghenycounty.legistar.com` in our example.



```python
county = noweba.NoWebA("alleghenycounty")
```

5. Now that we have most of the setup done, we can start making requests. Currently, our dictionary will only allow us to make one request, but we can make many if we continuously change a key of the dictionary. In our case, we are going to filter for specific boards in Allegheny County. To do this, we can make a list of boards and then loop through them, making a single request with a unique Text key for each one. For each piece of legislation we get in the rquest, it will stored internally as a dictionary with keys Title, Type, Status, File Created Date, Final Action Date, and GUID.


```python
county_boards = [
	"Redevelopment Authority of Allegheny County",
	"Retirement Board",
	"Southwestern Pennsylvania Commission",
	"Sports and Exhibition Authority",
	"Vacant Property Review Committee"
]

for board in county_boards:
	county_dict['Text'] = board
	county.singleRequest(county_dict)
```

### Part 2: Storing Data in Google Sheets
For this section, we'll be working with removesheet.py, another file in BoardExplorerLegistar. The RemoveSheet class allows you to create a Google Sheet that can be updated to move already seen items to a different sheet in the same spreadsheet. This requires usage of the Google Sheets API, which comes with substantial setup.

6. Before we can do any coding in Python, we need to set up permissions for our API with Google Cloud API services. To do this, first go to `console.developers.google.com` and log in with your Google Account. Now, click the Create Project button. You can name the project anything you want. Then, choose an organization and a location from the dropdown menus and click Create.

7. Now, it's time to configure the credentials. Go to 'OAuth consent screen' on the left menu and choose Internal or External. After entering basic information, choose to add scopes and manually add the scope `https://www.googleapis.com/auth/drive.file`. Then hit 'Update' and 'Save and Continue'. You can skip the optional info and then go back to the dashboard. If you chose External, make sure you are in the Testing stage and add yourself as a test user. To enable the Google Sheets API, go to the 'Enabled APIs & services' tab and hit '+ Enable APIs and Services.' Then, search for the Google Sheets API and enable it. For the last part of this step, go to the 'Credentials' tab and hit the '+ Create Credentials' button. Choose 'OAuth client ID', then 'Desktop app' and name it appropriately. Once you create the credentials, you should see a popup with an option at the bottom to 'Download JSON.' Hit that button. Rename the downloaded file to 'credentials.json' and move it to your working directory. Now, we are finally done configuring the API and its credentials.

8. Before we can work directly with removesheet.py, we need to install the Google client library for Python. Run the following command in the terminal: <br />
`pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

9. Now, we can import removesheet and create a RemoveSheet object, which we can use to update spreadsheet data. After importing removesheet, we try to get the current sheet. If there's no id.text file, we create a new spreadsheet instead.


```python
import removesheet

try:
	sheet = removesheet.getSheet()
except FileNotFoundError:
	sheet = removesheet.createSpreadsheet("Legistar Board Appointments", ["Title", "Type", "Status", "Date Passed", "GUID"])
```

10. Now, we need to write to our newly created spreadsheet. We can use the toSheets() method of our NoWebA instance to convert to a format that works well with Google Sheets. Then, we remove what we want to remove and write back to the actual sheet.


```python
county_sheet = county.toSheets(["Title", "Type", "Status", "Final Action Date", "GUID"])

#The 5 parameter tells the addRows method to check for duplicates based upon the fifth item (zero-indexed), which is GUID.
sheet.addRows(county_sheet, 5)
sheet.remove()
sheet.write()
```

### The End
Now, you should be able to run this code at any time and update your spreadsheet. The entirety of the code is below.


```python
import noweba
import removesheet
from datetime import datetime, timedelta

today = datetime.now().date()
one_year_ago = today - timedelta(days=365)

county_boards = [
	"Redevelopment Authority of Allegheny County",
	"Retirement Board",
	"Southwestern Pennsylvania Commission",
	"Sports and Exhibition Authority",
	"Vacant Property Review Committee"
]

county_dict = {
	"Type": "Appointment",
	"Status": "Approved",
	"Final Action Date": {
		"After": one_year_ago
	}
}

county = noweba.NoWebA("alleghenycounty")

for board in county_boards:
	county_dict['Text'] = board
	county.singleRequest(county_dict)

try:
	sheet = removesheet.getSheet()
except FileNotFoundError:
	sheet = removesheet.createSpreadsheet("Legistar Board Appointments", ["Title", "Type", "Status", "Date Passed", "GUID"])

county_sheet = county.toSheets(["Title", "Type", "Status", "Final Action Date", "GUID"])

sheet.addRows(county_sheet, 5)
sheet.remove()
sheet.write()
```
