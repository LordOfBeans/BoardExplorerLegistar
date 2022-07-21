import legisearch
import removesheet
from datetime import date

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

query_dict = {
	"Client": "pittsburgh",
	"MatterTypeName": [
		"Appointment-Requiring Vote",
		"Appointment-Informing"
	],
	"TitleContains": pittsburgh_boards1,
	"Date": {
		"Significance": "Passed",
		"After": date(2021, 7, 21)
	}
}

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
		"After": date(2021, 7, 21)
	}
}

dict2 = legisearch.fromDict(query_dict)

dict1.extend(dict2)

for board in pittsburgh_boards1 + pittsburgh_boards2:
	board_dict = dict1.titleContains(board)
	board_dict.addAttribute("Board", board)

sheet_values = dict1.toSheets(["Board", "MatterTitle", "MatterTypeName", "MatterStatusName", "MatterPassedDate", "MatterGuid"])

try:
	sheet = removesheet.getSheet()
except FileNotFoundError:
	sheet = removesheet.createSpreadsheet("Legistar Board Appointments", ["Board", "Title", "Type", "Status", "Date Passed", "GUID"])

sheet.addRows(sheet_values, 6)
sheet.remove()
sheet.write()