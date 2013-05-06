from flask import Flask, Response, request
from settings import *
from twilio.rest import TwilioRestClient
from random import choice
import sqlite3

app = Flask(__name__)

@app.route("/", methods=['POST'])
def root():
	# client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_TOKEN)
	# ([('FromZip', u'13346'), ('From', u'+13157505095'), ('FromCountry', u'US'), ('CalledCity', u'BROOKLYN'), ('CalledCountry', u'US'), ('Caller', u'+13157505095'), ('FromCity', u'HAMILTON'), ('ApiVersion', u'2010-04-01'), ('CallerCity', u'HAMILTON'), ('To', u'+19177464210'), ('CallSid', u'CAdff5ff58daa54260983b22ca08d2e615'), ('AccountSid', u'ACe5fc24ebf6cc903c8f35b751ebf33f79'), ('ToCity', u'BROOKLYN'), ('CalledState', u'NY'), ('FromState', u'NY'), ('CallerCountry', u'US'), ('CalledZip', u'11222'), ('Direction', u'inbound'), ('CallerZip', u'13346'), ('CallStatus', u'ringing'), ('Called', u'+19177464210'), ('CallerState', u'NY'), ('ToZip', u'11222'), ('ToCountry', u'US'), ('ToState', u'NY')])
	
	xml = '''
		<Response>
			<Gather action="/stepone" finishOnKey="12">
				<Say>Hello. Thanks for calling stranger.</Say>
		    	<Say>Press one to record a song.</Say>
	        	<Say>Press two and listen to a song.</Say>
    		</Gather>
    		<Redirect>%s</Redirect>
		</Response>
	      ''' % (IP)
	return Response(xml, mimetype='text/xml')

@app.route("/stepone", methods=['POST'])
def stepone():
	#([('Digits', u'1'), ('FromZip', u'13346'), ('From', u'+13157505095'), ('FromCountry', u'US'), ('CalledCity', u'BROOKLYN'), ('CalledCountry', u'US'), ('Caller', u'+13157505095'), ('FromCity', u'HAMILTON'), ('ApiVersion', u'2010-04-01'), ('CallerCity', u'HAMILTON'), ('To', u'+19177464210'), ('CallSid', u'CA8a70bcf6ce84979ec52877ee6fe9bf9f'), ('AccountSid', u'ACe5fc24ebf6cc903c8f35b751ebf33f79'), ('ToCity', u'BROOKLYN'), ('CalledState', u'NY'), ('FromState', u'NY'), ('CallerCountry', u'US'), ('CalledZip', u'11222'), ('Direction', u'inbound'), ('CallerZip', u'13346'), ('CallStatus', u'in-progress'), ('Called', u'+19177464210'), ('CallerState', u'NY'), ('ToZip', u'11222'), ('ToCountry', u'US'), ('msg', u'Gather End'), ('ToState', u'NY')])
	digits = request.form['Digits']

	if digits == '1':
		xml = '''
			<Response>
				<Say>Press any key to stop recording.</Say>
				<Record action="/record" playBeep="true" />
			</Response>
			  '''

	elif digits == '2':
			xml = '''
				<Response>
					<Redirect>%s/play</Redirect>
				</Response>
				  ''' % (IP)

	return Response(xml, mimetype='text/xml')

@app.route("/record", methods=['POST'])
def record():
	url = request.form['RecordingUrl']
	duration = request.form['RecordingDuration']
	calling_number = request.form['Caller']

	conn = sqlite3.connect(DB_NAME)
	cursor = conn.cursor()

	cursor.execute('''INSERT INTO songs VALUES ('%s', '%s', '%s')''' % (url, duration, calling_number))

	conn.commit()
	conn.close()

	xml = '''
		<Response>
			<Say>Thanks!</Say>
			<Redirect>%s</Redirect>
		</Response>
		  ''' % (IP)

	return Response(xml, mimetype='text/xml')

@app.route("/play", methods=['POST'])
def play():
	conn = sqlite3.connect(DB_NAME)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM songs;')
	voicemails = cursor.fetchall()
	conn.commit()
	conn.close()

	voicemail = choice(voicemails)

	xml = '''
		<Response>
			<Play>%s</Play>
			<Redirect>%s</Redirect>
		</Response>
		  ''' % (voicemail[0], IP)

	return Response(xml, mimetype='text/xml')

@app.route("/view", methods=['GET'])
def view():
	conn = sqlite3.connect(DB_NAME)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM songs;')
	voicemails = cursor.fetchall()
	conn.commit()
	conn.close()

	data = ''
	for voiceemail in voicemails:
		data += '<a href="%s">URL</a> - %s Seconds - From: %s <br><br>' % (voiceemail[0], voiceemail[1], voiceemail[2])

	return data

if __name__ == "__main__":
	if DEV_MODE:
		app.debug = True

	app.run(host='0.0.0.0')
