from pymongo import MongoClient
from dataservice import DataService
import operator
import math

class Helper(object):
	@classmethod
	def cosine_similarity(cls, app_list1, app_list2):
		match_count = cls.__count_match(app_list1, app_list2)
		return float(match_count) / math.sqrt( len(app_list1) * len(app_list2))

	@classmethod
	def __count_match(cls, list1, list2):
		count = 0
		for element in list1:
			if element in list2:
				count += 1
		return count

def calculate_top_5(app, user_download_history):
	# creat a dict to store each other app and its similarity to this app
	app_similarity = {} # (app_id : similarity)

	for apps in user_download_history:
		# calculate the similarity
		similarity = Helper.cosine_similarity([app], apps)
		for other_app in apps:
			if app_similarity.has_key(other_app):
				app_similarity[other_app] = app_similarity[other_app] + similarity
			else:
				app_similarity[other_app] = similarity

	# There could be app without related apps (not in any download history)
	if not app_similarity.has_key(app):
		return 

	# sort app similarity dict by value and get the top5 as recommendation
	app_similarity.pop(app) # pop app itself 
	sorted_tups = sorted(app_similarity.items(), key=operator.itemgetter(1), reverse = True) # sort by similarity
	top_5_app = [sorted_tups[0][0], sorted_tups[1][0], sorted_tups[2][0], sorted_tups[3][0], sorted_tups[4][0]]
	# print("top_5_app for" + str(app) + ":\t" + str(top_5_app))

	# store the top 5
	# update app delivered by filter  
	DataService.update_app_info({'app_id' : app}, {'$set': {'top_5_app': top_5_app}})


def main():
	# handle the connection with mongodb
	try: 
		# get MongoDB client and set it in DataService
		client = MongoClient('localhost', 27017)
		DataService.init(client)

		#work folow
		user_download_history = DataService.retrieve_user_download_history()

		app_info = DataService.retrieve_app_info()
		for app in app_info.keys():
			calculate_top_5(app, user_download_history.values())
	
	except Exception as e:
		print(e)
	finally:
		# clean up work
		if 'client' in locals():
			client.close()
if __name__ == "__main__":
	main()

