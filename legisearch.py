# LegiSearch class and additional methods for simple Legistar searches
# Built for used by PublicSource for Board Explorer
# By Sean Lord
# July 2022

from datetime import date
import json
import urllib.request
import urllib.parse
from copy import deepcopy

#Returns JSON response from querying Legistar with URL
def queryLegistar(url):
	req = urllib.request.Request(url)
	with urllib.request.urlopen(req) as resp:
		return json.loads(resp.read())
		

#Returns Legistar Web API URL from dictionary
def dictToQuery(query_dict):
	query_list = ["https://webapi.legistar.com/v1/"]

	#Required Client key takes String
	try:
		query_list.extend([query_dict["Client"], "/matters", "?$filter="])
	except KeyError:
		raise KeyError("Query dictionary is missing the Client key")

	#Optional TitleContains key takes String or list
	try:
		title_contains = query_dict["TitleContains"]
		if isinstance(title_contains, str):
			query_list.extend(["substringof('{}',MatterTitle)".format(title_contains), " and "])
		elif isinstance(title_contains, list) and len(title_contains) > 0:
			contains_list = ["("]
			for i in title_contains:
				contains_list.extend(["substringof('{}',MatterTitle)".format(i), " or "])
			contains_list[-1] = ")"
			query_list.extend(contains_list)
			query_list.append(" and ")
	except KeyError:
		pass

	#Optional Date key takes a dictionary with required Significance key along with optional Before and After keys
	sig_key_error = "Date key is missing nested Significance key"
	try:
		date_dict = query_dict["Date"]
		try:
			date_sig = date_dict["Significance"]
			if date_sig == "Modified":
				date_type = "MatterLastModifiedUtc"
			elif date_sig in ["Agenda", "Enactment", "Intro", "Passed"]:
				date_type = "Matter{}Date".format(date_sig)
			else:
				raise Error("Date significance type {} not recognized".format(date_sig))
		except KeyError:
			raise KeyError(sig_key_error)
		try:
			date_before = date_dict["Before"]
			query_list.extend(["{type} le datetime'{date}'".format(type=date_type, date = str(date_before)), " and "])
		except KeyError:
			pass
		try:
			date_after = date_dict["After"]
			query_list.extend(["{type} gt datetime'{date}'".format(type=date_type, date = str(date_after)), " and "])
		except KeyError:
			pass
	except KeyError as e:
		if e.args[0] == sig_key_error:
			raise e
		else:
			pass

	#Can use optional arbitrary query keys for equivalency where values are of type integer or string
	incompat_type_error = "Values for arbitrary query keys may only be integers or strings"
	for item in query_dict.items():
		if item[0] not in ["Client", "TitleContains", "Date"]:
			if isinstance(item[1], str):
				query_list.extend(["{key} eq '{value}'".format(key=item[0], value=item[1]), " and "])
			elif isinstance(item[1], int):
				query_list.extend(["{key} eq {value}".format(key=item[0], value=str(item[1])), " and "])
			elif isinstance(item[1], list) and len(item[1]) > 0:
				term_list = ["("]
				for i in item[1]:
					if isinstance(i, str):
						term_list.extend(["{key} eq '{value}'".format(key=item[0], value=i), " or "])
					elif isinstance(i, int):
						term_list.extend(["{key} eq {value}".format(key=item[0], value=str(i)), " or "])
					else:
						raise TypeError(incompat_type_error)
				term_list[-1] = ")"
				query_list.extend(term_list)
				query_list.append(" and ")
			else:
				raise TypeError(incompat_type_error)

	query_list.pop(-1)
	return urllib.parse.quote_plus("".join(query_list), safe="/:?=&$'(),")

#Returns LegiSearch instance after querying Legistar from query dictionary
def fromDict(query_dict):
	return LegiSearch(queryLegistar(dictToQuery(query_dict)))

#Returns LegiSearch instance after querying Legistar from URL with query parameters
def fromQueryURL(url):
	return LegiSearch(queryLegistar(url))

#Return LegiSearch instance directly from JSON data recieved from previous query
def fromJSON(json_data):
	return LegiSearch(json_data)

class LegiSearch:

	def __init__(self, json_data):
		self.json_data = json_data

	#Return a JSON respresentation of this LegiSearch object
	def toJSON(self):
		return deepcopy(self.json_data)

	#Return a deep copy of this LegiSearch object
	def copy(self):
		return LegiSearch(toJSON())

	#Take a string or a list of strings and returns a LegiSearch object with all items where title contains string/s
	def titleContains(self, contains):
		if isinstance(contains, str):
			contains_list = [x for x in self.json_data if contains in x["MatterTitle"]]
			return LegiSearch(contains_list)
		elif isinstance(contains, list):
			contains_list = []
			for contains_string in contains:
				contains_string_list = [x for x in self.json_data if contains_string in x["MatterTitle"]]
				contains_list.extend(contains_string_list)
			return LegiSearch(contains_list)
		else:
			raise Error("titleContains method only accepts string or list of string as parameter, not " + type(contains))

	#For every item in LegiSearch object, add an attribute with specified key and value
	def addAttribute(self, key, value):
		for item in self.json_data:
			item[key] = value

	#Return a 2D list representing a spreadsheet based on keys in column input
	#If key does not exist, fills space with an empty string
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