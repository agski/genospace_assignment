from flask import render_template, request, jsonify, url_for
from flask_pymongo import PyMongo
from app import app, mongo
from bson import ObjectId

@app.route('/', methods=['GET'])
@app.route('/index',methods=['GET'])
def index():
	# mongo.db.mechanisms.drop()
	# mongo.db.drugs.drop()
	# mongo.db.suggestions.drop()
	# mech_data1 = [{'name':'mech1'},{'name':'mech2'},{'name':'mech3'}]
	# mech_data2 = [{'name':'drech'}]
	# mech_ids1 = mongo.db.mechanisms.insert_many(mech_data1).inserted_ids
	# mech_ids2 = mongo.db.mechanisms.insert_many(mech_data2).inserted_ids
	# drug_data1 = [{'name':'drug1', 'mechanisms':['mech1','mech2'], 'mech_ids':[str(mech_ids1[0]),str(mech_ids1[1])]},
	# 		   {'name':'drug2', 'mechanisms':['mech2','mech3'], 'mech_ids':[str(mech_ids1[1]),str(mech_ids1[2])]},
	# 		   {'name':'meug', 'mechanisms':['mech2','mech3'], 'mech_ids':[str(mech_ids1[1]),str(mech_ids1[2])]}]

	# drug_data2 = {'name':'drug3', 'mechanisms':['drech','meug'], 'mech_ids':[str(mech_ids2)]}

	# drug_ids1 = mongo.db.drugs.insert_many(drug_data1).inserted_ids
	# drug_ids2 = mongo.db.drugs.insert_one(drug_data2).inserted_id
	# suggest_data1=[{'name':'drech', 'entry_id':str(mech_ids2),'popularity':1, 'type_of':'Mechanism'},
	# 			  {'name':'meug', 'entry_id':str(mech_ids2), 'popularity':2,'type_of':'Name'},
	# 			  {'name':'drug3', 'entry_id':str(drug_ids2), 'popularity':3,'type_of':'Name'}]

	# suggest_data2 =[{'name':'drug1', 'entry_id':str(drug_ids1[0]), 'popularity':4,'type_of':'Name'},
	# 			  {'name':'drug2', 'entry_id':str(drug_ids1[1]), 'popularity':5,'type_of':'Name'},
	# 			  {'name':'mech1', 'entry_id':str(mech_ids1[0]), 'popularity':6,'type_of':'Mechanism'},
	# 			  {'name':'mech2', 'entry_id':str(mech_ids1[1]), 'popularity':7,'type_of':'Mechanism'},
	# 			  {'name':'mech3', 'entry_id':str(mech_ids1[2]), 'popularity':8,'type_of':'Mechanism'}]

	# mongo.db.suggestions.insert_many(suggest_data1)
	# mongo.db.suggestions.insert_many(suggest_data2)
	print(mongo.db.collection_names(include_system_collections=False))
	return render_template('index.html')

@app.route('/autosuggest', methods=['POST'])
def autosuggest():
	query = request.form['query']
	options=[]
	if query != '':
		#Get matching suggestions from db
		options = list(mongo.db.suggestions.find({'name':{'$regex':'^'+query}}))
		options.sort(key=lambda x: x['popularity'], reverse=True)
		#Convert ObjectId to str (for jsonify), build url for suggestion
		for i in options:
			print(i['popularity'])
			i['_id']=str(i['_id'])
			i['url'] = url_for('details',type_of=i['type_of'],entry_id=i['entry_id'])
	return jsonify(options)

@app.route('/details/<type_of>/<entry_id>', methods=['GET','POST'])
def details(type_of, entry_id):
	drugs=[]
	#increment suggestion popularity score
	mongo.db.suggestions.update_one({'entry_id':entry_id}, {'$inc':{'popularity':1}})
	#query backend for relevant type of search, error otherwise
	if type_of == 'Name':
		drugs = list(mongo.db.drugs.find({'_id': ObjectId(entry_id)}))
	elif type_of == 'Mechanism':
		drugs = list(mongo.db.drugs.find({'mech_ids': entry_id}))
	else:
		return('Invalid type of search')

	#build drug url, convert ObjectId ids to strings
	for i in drugs:
		i['url'] = 'http://127.0.0.1:5000'+url_for('details',type_of='Name',entry_id=ObjectId(i['_id']))
		i['_id'] = str(i['_id'])

	#return as json if ajax POST request, render as template if GET
	if request.method == 'POST':
		return jsonify(drugs)
	return render_template('details.html',drugs=drugs)

def addDrug(record):
	#check if drug is new
	if mongo.db.drugs.find({'id':record.id}) != []:
		return
	#get drug name and mechanisms
	name = record.name
	mechs = record.mechs

	#get the new mechs
	new_mechs=[]
	stored = mongo.db.mechanisms.find()
	for i in mechs:
		if i not in stored:
			new_mechs += [i]

	#format as collection and insert new drug, get id
	drug_id = mongo.db.drugs.insert_one(formatted_record).inserted_id

	#format as collection and insert new mechanisms, get ids
	mech_ids = mongo.db.mechanisms.insert_many(formatted_mechs).inserted_ids

	#create and store new suggetsions for drug name and new mechanisms
	mongo.db.suggestions.insert_many(suggestions)

