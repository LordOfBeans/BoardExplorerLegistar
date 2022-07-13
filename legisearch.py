# LegiSearch class
# Built for simple Legistar searches
# By Sean Lord
# July 2022

from datetime import date
import json
import urllib.request
import urllib.parse

class LegiSearch:

	#Turns the query dictionary into a Legistar Web API url query
	@staticmethod
	def querySearch(query_data):
		query_list = ["https://webapi.legistar.com/v1/"]

		#Required Client key takes String
		try:
			query_list.extend([query_data["Client"], "/matters", "?$filter="])
		except KeyError:
			raise KeyError("Query dictionary is missing the Client key")

		#Optional TitleContains key takes String or list
		try:
			title_contains = query_data["TitleContains"]
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
			date_dict = query_data["Date"]
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
		for item in query_data.items():
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
		print(urllib.parse.quote_plus("".join(query_list), safe="/:?=&$'(),"))