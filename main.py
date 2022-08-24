import legisearch
import removesheet
from datetime import datetime, timedelta
import noweba

today = datetime.now().date()
one_year_ago = today - timedelta(days=365)

pittsburgh_boards1 = [
	"Art Commission",
	"Board of Appeals",
	"Board of License and Inspection Review",
	"Citizen Police Review Board",
	"City Planning Commission",
	"Civil Service Commission",
	"Clean Pittsburgh Commission",
	"Commission on Human Relations",
	"Commission on Racial Equality",
	"Comprehensive Municipal Pension Trust Fund",
	"Equal Opportunity Review Commission",
	"Equipment Leasing Authority",
	"Ethics Hearing Board"
]

pittsburgh_boards2= [
	"Gender Equity Commission",
	"Historic Review Commission",
	"Housing Authority",
	"LGBTQIA+ Commission",
	"Housing Opportunity Fund Advisory Board",
	"Partner4Work",
	"Pittsburgh Parking Authority",
	"Pittsburgh Shade Tree Commission",
	"Pittsburgh Water and Sewer Authority",
	"Stadium Authority",
	"Urban Redevelopment Authority",
	"Zoning Board of Adjustment"
]

county_boards = [
	"Accountability, Conduct and Ethics Commission",
	"Agricultural Land Preservation Board",
	"Air Pollution Control Advisory Committee",
	"Allegheny County Airport Authority",
	"Allegheny County Conservation District",
	"Allegheny County Housing Authority",
	"Allegheny County Human Relations Commission",
	"Allegheny County Sanitary Authority",
	"Allegheny Regional Asset District",
	"Area Agency on Aging Advisory Council",
	"Authority for Improvements in Municipalities",
	"Board of Health",
	"Carnegie Library of Pittsburgh Board of Trustees",
	"Children, Youth & Families Advisory Committee",
	"City-County Task Force on Disabilities",
	"Community College of Allegheny County",
	"Community Services Advisory Council",
	"Drug & Alcohol Planning Council",
	"Elections Board",
	"Finance and Development Commission",
	"Independent Police Review Board",
	"Jail Oversight Board",
	"Juvenile Detention Board",
	"MBE Advisory Committee",
	"Mental Health/Intellectual Disability Advisory Board",
	"Partner4Work",
	"Personnel Board",
	"Pittsburgh Regional Transit",
	"Professional Services Review Committee",
	"Property Assessment Appeals & Review Board",
	"Redevelopment Authority of Allegheny County",
	"Retirement Board",
	"Southwestern Pennsylvania Commission",
	"Sports and Exhibition Authority",
	"Vacant Property Review Committee"
]

query_dict = {
	"Client": "pittsburgh",
	"MatterTypeName": [
		"Appointment-Requiring Vote",
		"Appointment-Informing"
	],
	"TitleContains": pittsburgh_boards1,
	"Date": {
		"Significance": "Passed",
		"After": one_year_ago
	}
}

print("Making first request for Pittsburgh boards")
dict1 = legisearch.fromDict(query_dict)

query_dict = {
	"Client": "pittsburgh",
	"MatterTypeName": [
		"Appointment-Requiring Vote",
		"Appointment-Informing"
	],
	"TitleContains": pittsburgh_boards2,
	"Date": {
		"Significance": "Passed",
		"After": one_year_ago
	}
}

print("Making second request for Pittsburgh boards")
dict2 = legisearch.fromDict(query_dict)

dict1.extend(dict2)

for board in pittsburgh_boards1 + pittsburgh_boards2:
	board_dict = dict1.titleContains(board)
	board_dict.addAttribute("Board", board)

county_dict = {
	"Type": "Appointment",
	"Status": "Approved",
	"Final Action Date": {
		"After": one_year_ago
	}
}

county = noweba.NoWebA("alleghenycounty")
for board in county_boards:
	print("Requesting data for " + board)
	county_dict['Text'] = board
	county.singleRequest(county_dict)

for board in county_boards:
	county.addTitleAttribute("Board", board, board)

city_sheet = dict1.toSheets(["Board", "MatterTitle", "MatterTypeName", "MatterStatusName", "MatterPassedDate", "MatterGuid"])
county_sheet = county.toSheets(["Board", "Title", "Type", "Status", "Final Action Date", "GUID"])

sheet_values = city_sheet + county_sheet

try:
	sheet = removesheet.getSheet()
except FileNotFoundError:
	sheet = removesheet.createSpreadsheet("Legistar Board Appointments", ["Board", "Title", "Type", "Status", "Date Passed", "GUID"])

sheet.addRows(sheet_values, 6)
sheet.remove()
sheet.write()