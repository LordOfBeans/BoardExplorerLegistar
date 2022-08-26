# RemoveSheet class and related methods
# Built to create two sheets in a spreadsheet, one with new data and one with data that has already been dealt with
# By Sean Lord
# July 2022


import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions

# If true, changes row background color to light gray if there's an x in column A
# Only works for columns A to Z and rows 2 to 1000
# I recommend turning this off if more columns or rows are needed
# Should also be turned off if experiencing lag
HIGHLIGHT_REMOVE = True

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# From Google's Python Quickstart for Sheets API
creds = None

if os.path.exists('token.json'):
	creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
	flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
	creds = flow.run_local_server(port=0)
	with open('token.json', 'w') as token:
		token.write(creds.to_json())
try:
	service = build('sheets', 'v4', credentials=creds)
	sheetsAPI = service.spreadsheets()
except HttpError as e:
	print(e)

def newToken():
	flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
	creds = flow.run_local_server(port=0)
	with open('token.json', 'w') as token:
		token.write(creds.to_json())
	try:
		service = build('sheets', 'v4', credentials=creds)
		sheetsAPI = service.spreadsheets()
	except HttpError as e:
		print(e)

# Creates a spreadsheet and returns a new instance of RemoveSheet
# column_names parameter takes a list of strings
def createSpreadsheet(title, column_names):

	#Specify title and create new spreadsheet
	create_body = {
		'properties': {
			'title': title
		}
	}
	new_spreadsheet = sheetsAPI.create(body=create_body, fields='spreadsheetId').execute()
	id = new_spreadsheet['spreadsheetId']
	data_range = "A2:J1000"

	#Create and format new sheets with only column names
	column_values = []
	for name in ['Remove'] + column_names:
		cell_value = {
			'userEnteredValue': {
				'stringValue': name
			},
			'userEnteredFormat': {
				'textFormat': {
					'bold': True
				}
			}
		}
		column_values.append(cell_value)
	update_body = {
		'requests': [
			{
				'updateSheetProperties': {
					'properties': {
						'title': 'New',
						'sheetId': 0,
						'gridProperties': {
							'frozenRowCount': 1
						}
					},
					'fields': 'title, gridProperties.frozenRowCount'	
				}
			},
			{
				'updateCells': {
					'rows': [
						{
							'values': column_values
						}
					],
					'fields': 'userEnteredValue, userEnteredFormat',
					'start': {
						'sheetId': 0,
						'rowIndex': 0,
						'columnIndex': 0
					}	
				}
			},
			{
				'duplicateSheet': {
					'sourceSheetId': 0,
					'insertSheetIndex': 1,
					'newSheetId': 1,
					'newSheetName': 'Removed'
				}
			}
		]
	}

	#Enabled or disabled based upon HIGHLIGHT_REMOVE
	row_highlighting = {
		'addConditionalFormatRule': {
			'rule': {
				'ranges': [
					{
						'sheetId': 0,
						'startRowIndex': 1,
						'endRowIndex': 999,
						'startColumnIndex': 0,
						'endColumnIndex': 25
					}
				],
				'booleanRule': {
					'condition': {
						'type': 'CUSTOM_FORMULA',
						'values': [
							{
								'userEnteredValue': '=EQ($A2, \"x\")'
							}
						]
					},
					'format' : {
						'backgroundColorStyle': {
							'rgbColor': {
								'red': 75,
								'green': 75,
								'blue': 75
							}
						}
					}
				}
			},
			'index': 0
		}
	}
	if HIGHLIGHT_REMOVE:
		update_body['requests'].insert(-2, row_highlighting)
				
	sheetsAPI.batchUpdate(spreadsheetId = id, body=update_body).execute()
	with open('spreadsheetId.txt', 'w') as id_file:
		id_file.write(id)
	return RemoveSheet(id, [], [], data_range)

#Returns a RemoveSheet object and reads id from 'spreadsheetId.txt'
def getSheet():
	with open('spreadsheetId.txt', 'r') as id_file:
		id = id_file.read()
	try:
		get_new = sheetsAPI.values().get(spreadsheetId = id, range = 'New').execute()
	except google.auth.exceptions.RefreshError:
		newToken()
		get_new = sheetsAPI.values().get(spreadsheetId = id, range = 'New').execute()
	get_remove = sheetsAPI.values().get(spreadsheetId = id, range = 'Removed').execute()
	new_values = get_new['values'][1:]
	remove_values = get_remove['values'][1:]
	data_range = "A2" + get_new['range'][6:]
	return RemoveSheet(id, new_values, remove_values, data_range)

class RemoveSheet:

	def __init__(self, id, news, removes, range):
		self.spreadsheet_id = id
		self.new_values = news
		self.remove_values = removes
		self.data_range = range

	#Checks for identical values in dupe_column, where index 0 is the 'Remove' column
	def addRows(self, rows, dupe_column):
		all_values = self.new_values + self.remove_values
		for new_row in rows:
			dupe_list = [row for row in all_values if new_row[dupe_column - 1] == row[dupe_column]]
			if len(dupe_list) == 0:
				append_row = [''] + new_row
				all_values.append(append_row)
				self.new_values.append(append_row)

	def write(self):
		new_body = {'values': self.new_values}
		remove_body = {'values': self.remove_values}
		sheetsAPI.values().clear(spreadsheetId = self.spreadsheet_id, range = 'New!' + self.data_range).execute()
		sheetsAPI.values().update(spreadsheetId=self.spreadsheet_id,  range='New!' + self.data_range, body=new_body, valueInputOption='USER_ENTERED').execute()
		sheetsAPI.values().clear(spreadsheetId=self.spreadsheet_id,  range='Removed!' + self.data_range).execute()
		sheetsAPI.values().update(spreadsheetId=self.spreadsheet_id,  range='Removed!' + self.data_range, body=remove_body, valueInputOption='USER_ENTERED').execute()

	def remove(self):
		i = 0
		while i < len(self.new_values):
			if self.new_values[i][0].lower() == 'x':
				self.remove_values.append(self.new_values.pop(i))
			else:
				i += 1
		i= 0
		while i < len(self.remove_values):
			if self.remove_values[i][0].lower() != 'x':
				self.new_values.append(self.remove_values.pop(i))
			else:
				i += 1
				
				
		
		
		
		
	