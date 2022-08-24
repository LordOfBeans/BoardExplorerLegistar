#Written by Sean Lord

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import datetime
import time

class NoWebA:
	json_data = []
	
	def __init__(self, client):
		#Dictionary contains values that allow me to get to the Advanced Search
		advanced_dict = {
			'__EVENTTARGET': "",
			'__EVENTARGUMENT': "",
			'ctl00_tabTop_ClientState': "{\"selectedIndexes\":[\"1\"],\"logEntries\":[],\"scrollState\":{}}",
			'ctl00_ContentPlaceHolder1_RadToolTipManager1_ClientState': "",
			'ctl00$ContentPlaceHolder1$txtSearch': "",
			'ctl00$ContentPlaceHolder1$lstYears': "All+Years",
			'ctl00_ContentPlaceHolder1_lstYears_ClientState': "",
			'ctl00$ContentPlaceHolder1$lstTypeBasic': "All+Types",
			'ctl00_ContentPlaceHolder1_lstTypeBasic_ClientState': "",
			'ctl00$ContentPlaceHolder1$chkID': "on",
			'ctl00$ContentPlaceHolder1$chkText': "on",
			'ctl00$ContentPlaceHolder1$btnSwitch': "Advanced+search+>>>",
			'ctl00_ContentPlaceHolder1_menuMain_ClientState': "",
			'ctl00_ContentPlaceHolder1_gridMain_ClientState': ""
		}

		self.url = "https://" + client + ".legistar.com/Legislation.aspx"
		req = urllib.request.Request(self.url)
		with urllib.request.urlopen(req) as resp:
			soup = BeautifulSoup(resp, 'html.parser')

		advanced_dict['ctl00_RadScriptManager1_TSM'] = soup.find('input', {'id': 'ctl00_RadScriptManager1_TSM'}).get('value')
		advanced_dict['__VIEWSTATE'] = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
		advanced_dict['__VIEWSTATEGENERATOR'] = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value')
		advanced_dict['__PREVIOUSPAGE'] = soup.find('input', {'id': '__PREVIOUSPAGE'}).get('value')
		req = urllib.request.Request(self.url, data = urllib.parse.urlencode(advanced_dict).encode())
		with urllib.request.urlopen(req) as resp:
			soup = BeautifulSoup(resp, 'html.parser')

		self.rad_script_manager = soup.find('input', {'id': 'ctl00_RadScriptManager1_TSM'}).get('value')
		self.viewstate = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
		self.viewstate_generator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value')
		self.previous_page = soup.find('input', {'id': '__PREVIOUSPAGE'}).get('value')

		self.sponsors = NoWebA.findPairs(soup, 'ctl00_ContentPlaceHolder1_lstSponsoredBy')
		self.types = NoWebA.findPairs(soup, 'ctl00_ContentPlaceHolder1_lstType')
		self.statuses = NoWebA.findPairs(soup, 'ctl00_ContentPlaceHolder1_lstStatus')
		self.controllers = NoWebA.findPairs(soup, 'ctl00_ContentPlaceHolder1_lstInControlOf')
		self.indexes = NoWebA.findPairs(soup, 'ctl00_ContentPlaceHolder1_lstIndexedUnder')


	def singleRequest(self, basic_dict):
		req_dict = {
			"ctl00_RadScriptManager1_TSM": self.rad_script_manager,
			"__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnSearch",
			"__EVENTARGUMENT": "",
			"__VIEWSTATE": self.viewstate,
			"__VIEWSTATEGENERATOR": self.viewstate_generator,
			"__PREVIOUSPAGE": self.previous_page,
			"ctl00_tabTop_ClientState": "{\"selectedIndexes\":[\"1\"],\"logEntries\":[],\"scrollState\":{}}",
			"ctl00_ContentPlaceHolder1_RadToolTipManager1_ClientState": "",
			"ctl00$ContentPlaceHolder1$lstMax": "All",
			"ctl00_ContentPlaceHolder1_lstMax_ClientState": "{\"logEntries\":[],\"value\":\"1000000\",\"text\":\"All\",\"enabled\":true,\"checkedIndices\":[],\"checkedItemsTextOverflows\":false}",
			"ctl00$ContentPlaceHolder1$lstYearsAdvanced": "All+Years",
			"ctl00_ContentPlaceHolder1_lstYearsAdvanced_ClientState": "{\"logEntries\":[],\"value\":\"All\",\"text\":\"All+Years\",\"enabled\":true,\"checkedIndices\":[],\"checkedItemsTextOverflows\":false}",
			"ctl00$ContentPlaceHolder1$txtText": "",
			"ctl00$ContentPlaceHolder1$txtTit": "",
			"ctl00$ContentPlaceHolder1$txtFil": "",
			"ctl00$ContentPlaceHolder1$lstType": "-Select-",
			"ctl00_ContentPlaceHolder1_lstType_ClientState": "",
			"ctl00$ContentPlaceHolder1$lstStatus": "-Select-",
			"ctl00_ContentPlaceHolder1_lstStatus_ClientState": "",
			"ctl00$ContentPlaceHolder1$txtFileCreated1": "",
			"ctl00$ContentPlaceHolder1$txtFileCreated1$dateInput": "",
			"ctl00_ContentPlaceHolder1_txtFileCreated1_dateInput_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"\"}",
			"ctl00_ContentPlaceHolder1_txtFileCreated1_calendar_SD": "[]",
			"ctl00_ContentPlaceHolder1_txtFileCreated1_calendar_AD": "[[1980,1,1],[2099,12,30],[2022,8,20]]",
			"ctl00_ContentPlaceHolder1_txtFileCreated1_ClientState": "",
			"ctl00$ContentPlaceHolder1$radFileCreated": "=",
			"ctl00$ContentPlaceHolder1$txtFileCreated2": "",
			"ctl00$ContentPlaceHolder1$txtFileCreated2$dateInput": "",
			"ctl00_ContentPlaceHolder1_txtFileCreated2_dateInput_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"\"}",
			"ctl00_ContentPlaceHolder1_txtFileCreated2_calendar_SD": "[]",
			"ctl00_ContentPlaceHolder1_txtFileCreated2_calendar_AD": "[[1980,1,1],[2099,12,30],[2022,8,20]]",
			"ctl00_ContentPlaceHolder1_txtFileCreated2_ClientState": "",
			"ctl00$ContentPlaceHolder1$lstInControlOf": "-Select-",
			"ctl00_ContentPlaceHolder1_lstInControlOf_ClientState": "",
			"ctl00$ContentPlaceHolder1$txtOnAgenda1": "",
			"ctl00$ContentPlaceHolder1$txtOnAgenda1$dateInput": "",
			"ctl00_ContentPlaceHolder1_txtOnAgenda1_dateInput_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"\"}",
			"ctl00_ContentPlaceHolder1_txtOnAgenda1_calendar_SD": "[]",
			"ctl00_ContentPlaceHolder1_txtOnAgenda1_calendar_AD": "[[1980,1,1],[2099,12,30],[2022,8,20]]",
			"ctl00_ContentPlaceHolder1_txtOnAgenda1_ClientState": "",
			"ctl00$ContentPlaceHolder1$radOnAgenda": "=",
			"ctl00$ContentPlaceHolder1$txtOnAgenda2": "",
			"ctl00$ContentPlaceHolder1$txtOnAgenda2$dateInput": "",
			"ctl00_ContentPlaceHolder1_txtOnAgenda2_dateInput_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"\"}",
			"ctl00_ContentPlaceHolder1_txtOnAgenda2_calendar_SD": "[]",
			"ctl00_ContentPlaceHolder1_txtOnAgenda2_calendar_AD": "[[1980,1,1],[2099,12,30],[2022,8,20]]",
			"ctl00_ContentPlaceHolder1_txtOnAgenda2_ClientState": "",
			"ctl00$ContentPlaceHolder1$txtFinalAction1": "",
			"ctl00$ContentPlaceHolder1$txtFinalAction1$dateInput": "",
			"ctl00_ContentPlaceHolder1_txtFinalAction1_dateInput_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"\"}",
			"ctl00_ContentPlaceHolder1_txtFinalAction1_calendar_SD": "[]",
			"ctl00_ContentPlaceHolder1_txtFinalAction1_calendar_AD": "[[1980,1,1],[2099,12,30],[2022,8,20]]",
			"ctl00_ContentPlaceHolder1_txtFinalAction1_ClientState": "",
			"ctl00$ContentPlaceHolder1$radFinalAction": "=",
			"ctl00$ContentPlaceHolder1$txtFinalAction2": "",
			"ctl00$ContentPlaceHolder1$txtFinalAction2$dateInput": "",
			"ctl00_ContentPlaceHolder1_txtFinalAction2_dateInput_ClientState": "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"\",\"valueAsString\":\"\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"\"}",
			"ctl00_ContentPlaceHolder1_txtFinalAction2_calendar_SD": "[]",
			"ctl00_ContentPlaceHolder1_txtFinalAction2_calendar_AD": "[[1980,1,1],[2099,12,30],[2022,8,20]]",
			"ctl00_ContentPlaceHolder1_txtFinalAction2_ClientState": "",
			"ctl00$ContentPlaceHolder1$lstSponsoredBy": "-Select-",
			"ctl00_ContentPlaceHolder1_lstSponsoredBy_ClientState":	"",
			"ctl00$ContentPlaceHolder1$lstIndexedUnder": "-Select-",
			"ctl00_ContentPlaceHolder1_lstIndexedUnder_ClientState": "",
			"ctl00$ContentPlaceHolder1$lstAffectsCodeSections": "-Select-",
			"ctl00_ContentPlaceHolder1_lstAffectsCodeSections_ClientState": "",
			"ctl00$ContentPlaceHolder1$txtAtt": "",
			"ctl00_ContentPlaceHolder1_menuMain_ClientState": "",
			"ctl00_ContentPlaceHolder1_gridMain_ClientState":""
		}


		#Checks for all the keys used in basic_dict and updates req_dict to use these specifications
		if 'Text' in basic_dict:
			req_dict["ctl00$ContentPlaceHolder1$txtText"] = basic_dict['Text']
		if 'Title' in basic_dict:
			req_dict["ctl00$ContentPlaceHolder1$txtTit"] = basic_dict['Title']
		if 'Type' in basic_dict:
			selection = basic_dict['Type']
			if selection in self.types:
				req_dict["ctl00$ContentPlaceHolder1$lstType"] = selection
				req_dict["ctl00_ContentPlaceHolder1_lstType_ClientState"] = "{\"logEntries\":[],\"value\":\"" + self.types[selection] + "\",\"text\":\"" + selection + "\",\"enabled\":true,\"checkedIndices\":[],\"checkedItemsTextOverflows\":false}"
		if 'Status' in basic_dict:
			selection = basic_dict['Status']
			if selection in self.statuses:
				req_dict["ctl00$ContentPlaceHolder1$lstStatus"] = selection
				req_dict["ctl00_ContentPlaceHolder1_lstStatus_ClientState"] = "{\"logEntries\":[],\"value\":\"" + self.statuses[selection] + "\",\"text\":\"" + selection + "\",\"enabled\":true,\"checkedIndices\":[],\"checkedItemsTextOverflows\":false}"
		if 'Index' in basic_dict:
			selection = basic_dict['Index']
			if status in self.indexes:
				req_dict["ctl00$ContentPlaceHolder1$lstIndexedUnder"] = selection
				req_dict["ctl00_ContentPlaceHolder1_lstIndexedUnder_ClientState"] = "{\"logEntries\":[],\"value\":\"" + self.indexes[selection] + "\",\"text\":\"" + selection + "\",\"enabled\":true,\"checkedIndices\":[],\"checkedItemsTextOverflows\":false}"
		if 'Controller' in basic_dict:
			selection = basic_dict['Controller']
			if status in self.indexes:
				req_dict["ctl00$ContentPlaceHolder1$lstInControlOf"] = selection
				req_dict["ctl00_ContentPlaceHolder1_lstInControlOf_ClientState"] = "{\"logEntries\":[],\"value\":\"" + self.controllers[selection] + "\",\"text\":\"" + selection + "\",\"enabled\":true,\"checkedIndices\":[],\"checkedItemsTextOverflows\":false}"
		if 'Sponsor' in basic_dict:
			selection = basic_dict['Controller']
			if status in self.sponsors:
				req_dict["ctl00$ContentPlaceHolder1$lstSponsoredBy"] = selection
				req_dict["ctl00_ContentPlaceHolder1_lstInControlOf_SponsoredBy"] = "{\"logEntries\":[],\"value\":\"" + self.sponsors[selection] + "\",\"text\":\"" + selection + "\",\"enabled\":true,\"checkedIndices\":[],\"checkedItemsTextOverflows\":false}"
		if 'Final Action Date' in basic_dict:
			nested_dict = basic_dict['Final Action Date']
			if 'Before' in nested_dict:
				before = nested_dict['Before']
				if 'After' in nested_dict:
					self.setDateKeys(req_dict, 'FinalAction', nested_dict['After'], before, 'between')
				else:
					self.setDateKeys(req_dict, 'FinalAction', before, datetime.datetime.now(), '<')
			elif 'After' in nested_dict:
				self.setDateKeys(req_dict, 'FinalAction', nested_dict['After'], datetime.datetime.now(), '>')

		soup = self.postRequest(req_dict)

		#Allow for multiple pages to be searched through
		page_table = soup.find('table', {'summary': 'Data pager which controls on which page is the RadGrid control.'})
		if page_table != None:
			button_holder = page_table.tbody.tr.td.div
			while True:
				next_button = button_holder.find('a', {'class':'rgCurrentPage'}).next_sibling
				if next_button.name == 'a':
					req_dict['__VIEWSTATE'] = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
					req_dict['__VIEWSTATEGENERATOR'] = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value')
					req_dict['__EVENTTARGET'] = next_button.get('href')[25:83]
					soup = self.postRequest(req_dict)
					matters = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gridMain_ctl00'}).contents[5].children
					for matter in matters:
						if matter != '\n':
							self.matterSoupToData(matter)
					page_table = soup.find('table', {'summary': 'Data pager which controls on which page is the RadGrid control.'})
					button_holder = page_table.tbody.tr.td.div
				else:
					break
		else:
			matters = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gridMain_ctl00'}).contents[4].children
			for matter in matters:
				if matter != '\n':
					self.matterSoupToData(matter)

	#Extracts Title, Type, Status, File Created, Final Action Date, and GUID
	def matterSoupToData(self, matter_soup):
		matter_dict = {}

		matter_elements = matter_soup.contents
		try:
			try:
				matter_dict['Type'] = matter_elements[2].font.string
			except AttributeError:
				pass
			matter_dict['Status'] = matter_elements[3].font.string
			try:
				matter_dict['File Created Date'] = matter_elements[4].font.string
			except ValueError:
				pass
			try:
				matter_dict['Final Action Date'] = matter_elements[5].font.string
			except ValueError:
				pass
			matter_dict['Title'] = matter_elements[6].font.string
			matter_href = matter_elements[1].font.a.get('href')
			try:
				matter_dict['GUID'] = matter_href[matter_href.index('GUID') + 5: matter_href.index('&Options=Advanced&Search=')]
			except AttributeError:
				pass
			self.json_data.append(matter_dict)
		except IndexError:
			pass

	#Makes a post request and returns soup
	#If connection is reset, waits a bit and then tries again
	def postRequest(self, post_dict):
		req = urllib.request.Request(self.url, data = urllib.parse.urlencode(post_dict).encode())
		try:
			with urllib.request.urlopen(req) as resp:
				return BeautifulSoup(resp, 'html.parser')
		except ConnectionResetError:
			print("Connection reset by server. Trying again in 5 seconds.")
			time.sleep(5)
			return self.postRequest(post_dict)

	def setDateKeys(self, req_dict, date_type, date1, date2, sign):
		req_dict["ctl00$ContentPlaceHolder1$rad" + date_type] = sign
		req_dict["ctl00$ContentPlaceHolder1$txt" + date_type + "1"] = date1.strftime("%Y-%m-%d")
		req_dict["ctl00$ContentPlaceHolder1$txt" + date_type + "2"] = date2.strftime("%Y-%m-%d")
		req_dict["ctl00$ContentPlaceHolder1$txt" + date_type + "1$dateInput"] = "{date.month}/{date.day}/{date.year}".format(date = date1)
		req_dict["ctl00$ContentPlaceHolder1$txt" + date_type + "2$dateInput"] = "{date.month}/{date.day}/{date.year}".format(date = date2)
		full_date1_string = date1.strftime('%Y-%m-%d-%H-%M-%S')
		full_date2_string = date2.strftime('%Y-%m-%d-%H-%M-%S')
		req_dict["ctl00_ContentPlaceHolder1_txt" + date_type + "1_dateInput_ClientState"] = "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"" + full_date1_string + "\",\"valueAsString\":\"" + full_date1_string + "\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"" + req_dict["ctl00$ContentPlaceHolder1$txt"+ date_type + "1$dateInput"] + "\"}"
		req_dict["ctl00_ContentPlaceHolder1_txt" + date_type + "2_dateInput_ClientState"] = "{\"enabled\":true,\"emptyMessage\":\"\",\"validationText\":\"" + full_date2_string + "\",\"valueAsString\":\"" + full_date2_string + "\",\"minDateStr\":\"1980-01-01-00-00-00\",\"maxDateStr\":\"2099-12-31-00-00-00\",\"lastSetTextBoxValue\":\"" + req_dict["ctl00$ContentPlaceHolder1$txt"+ date_type + "2$dateInput"] + "\"}"

	@staticmethod
	def findPairs(soup, name):
		form_script = soup.form.find_all('script', {'type':'text/javascript'})[2].string
		sponsors = soup.find('div', {'id': name + '_DropDown'}).div.ul.contents[1:]
		area = form_script[form_script.index(name):form_script.index('$get(\"' + name + '\")')]
		value_start = area[area.index('{\"value\":\"') + 10:]
		values_split = value_start.split('\"},{\"value\":\"')
		values = values_split[:-1]
		values.append(values_split[-1][:values_split[-1].index('\"}]')])
		return_dict = {}
		for i in range(0, len(values)):
			return_dict[sponsors[i].string] = values[i]
		return return_dict

	#Return a 2D list representing a spreadsheet based on keys in column input
	#If key does not exist, fills space with an empty string
	#Identical to that of LegiSearch class
	def toSheets(self, column_keys):
		row_list = []
		for item in self.json_data:
			one_row = []
			for key in column_keys:
				try:
					one_row.append(item[key])
				except KeyError:
					one_row.append("")
			row_list.append(one_row)
		return row_list

	def addTitleAttribute(self, attribute_name, title_text, add_text):
		for matter in self.json_data:
			try:
				if title_text.lower() in matter['Title'].lower():
					matter[attribute_name] = add_text
			except KeyError:
				pass
				
			
		
 