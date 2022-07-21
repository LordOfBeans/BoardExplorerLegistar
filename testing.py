import legisearch
from datetime import date
import removesheet

query_dict = {
	"Client": "pittsburgh",
	"MatterTypeName": [
		"Appointment-Requiring Vote",
		"Appointment-Informing"
	],
	"TitleContains": [
		"Urban Redevelopment Authority",
		"Zoning Board of Adjustment",
		"Stadium Authority",
		"Pittsburgh Shade Tree Commission"
	],
	"Date": {
		"Significance": "Passed",
		"After": date(2020, 1, 1)
	}
}

queryURL = legisearch.dictToQuery(query_dict)
all = legisearch.fromQueryURL(queryURL)
ura = all.titleContains("Urban Redevelopment Authority")
ura.addAttribute("Board", "Urban Redevelopment Authority")

sheets_format = all.toSheets(["Board", "MatterTitle", "MatterPassedDate", "MatterGuid"])

board_sheet = removesheet.getSheet()
board_sheet.addRows(sheets_format, 4)
board_sheet.remove()
board_sheet.write()
