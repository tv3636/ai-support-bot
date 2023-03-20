import os
import discord
import openai
import json
import requests
from dotenv import load_dotenv
from retry import retry

load_dotenv()

openai.api_key = os.getenv('OPENAI_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RESERVOIR_DOCS_BASE_URL = "https://docs.reservoir.tools/docs/"
client = discord.Client()

# Headers to scrape readme.io docs
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Google Chrome\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://docs.reservoir.tools/docs",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Slugs for all Reservoir docs
slugs = [
	'what-is-reservoir',
	'supported-marketplaces',
	'supported-chains',
	'faq',
	'nft-liquidity-router',
	'data-lake',
	'indexer',
	'marketplace-toolkit',
	'typescript-api-typings',
	'buytoken',
	'listtoken',
	'placebid',
	'acceptoffer',
	'cancelorder',
	'sweeping',
	'buying',
	'listing',
	'bidding',
	'accept-bid',
	'add-a-cart',
	'cancel-a-listing',
	'cancel-a-listing-1',
	'reservoir-kit-theming-and-customization',
	'tokenmedia',
	'rk-ui-troubleshooting',
	'reservoirkit-ui',
	'reservoir-sdk',
	'usetokens',
	'usecollections',
	'usecollectionactivity',
	'useusersactivity',
	'usetokenactivity',
	'uselistings',
	'useownerlistings',
	'usereservoirclient',
	'detect-tokens-flagged-by-opensea',
	'useattributes',
	'usebids',
	'useusertopbids',
	'useusercollections',
	'useusertokens',
	'usecart',
	'usedynamictokens',
	'marketplace',
	'custom-marketplaces',
	'aggregated-liquidity',
	'data-and-analytics',
	'market-making',
	'understanding-sales',
	'filling-existing-liquidity',
	'full-support',
	'walletportfolio-app',
	'calldata-attribution',
	'add-instant-sell',
	'buy-sweep',
	'bulk-order-creation',
	'floor-prices',
	'adding-support-for-custom-erc-20-token',
	'flagged-tokens',
	'royalties',
	'custom-fees',
	'realtime-websocket-events',
	'hosting-a-reservoir-discord-nft-bot',
	'accessing-native-liquidity',
	'hosted-vs-self-hosted',
	'filling-orders-explainer',
	'marketplace-fees-royalties',
	'blur-limitations',
	'built-on-reservoir',
	'security-and-smart-contract-audits',
	'glossary',
	'logos'	
]

# Simple logger to prepend logs with an identifying component name
def log(component, message):
	print(component + ': ' + str(message))

# Returns true if the input is a valid JSON object. Otherwise returns false.
def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

# Returns the body of a Reservoir doc given the doc's slug. If the doc can't be loaded, defaults to previously saved doc on disc.
def getDocForSlug(slug):
	try:
		headers['Referer'] = RESERVOIR_DOCS_BASE_URL + slug
		response = requests.get(RESERVOIR_DOCS_BASE_URL + slug + '?json=on', headers=headers)
		
		log('readme-response', response)
		return slug + ':\n' + response.json()['doc']['body']

	except Exception as e:
		log('error', "could not load doc for slug " + slug)
		log('error', e)

		try:
			f = open('docs/%s.json' % slug)
			return slug + ':\n' + json.load(f)['doc']['body']
		except Exception as e:
			log('error', "could not load doc " + slug + ".json")
			log('error', e)

	return ''

# Returns an OpenAI completion for a given set of messages
@retry(Exception, tries=5, delay=1)
def getCompletionForMessages(messages):
	print("prompt: " + str(messages))
	response = openai.ChatCompletion.create(
  		model="gpt-4",
		messages=messages,
		temperature=0.5,
		max_tokens=2000
	)

	return response['choices'][0]['message']['content']

# Returns an AI response for a given question
def answerQuestion(question):
	try:
		messages = [
		    {"role": "system", "content": "You are a search assistant for the Reservoir API docs. You respond to user questions with only a JSON list of relevant doc names. The doc names to choose from are: " + ', '.join([slug for slug in slugs])},
		    {"role": "user", "content": question},
		    {"role": "user", "content": "respond with only a JSON list of at most the 5 most relevant doc names and nothing else"}
		]

		response = getCompletionForMessages(messages)
		log('openai-response', response)

		if (is_json(response)):
			docString = ''
			for slug in json.loads(response):
				docString += getDocForSlug(slug)

			messages = [
				{"role": "system", "content": "You are a friendly and helpful user support agent for the Reservoir API. You use the Reservoir API docs to answer user questions."},
				{"role": "user", "content": "Here are some relevant docs to help answer user questions: %s" % ' '.join(docString.split()[:6000])},
				{"role": "user", "content": question}
			]

			response = getCompletionForMessages(messages)
			log('openai-response', response)
			return response
		else:
			log('error', "could not get proper doc list")

	except Exception as e:
		log('error', "failed to get AI response for user question")
		log('error', e)

	# Catch-all response if AI response could not be generated
	return 'Unfortunately I was unable to find a sufficient answer to your question. The Reservoir team will get back to you as soon as possible.'


######################
# Discord bot events #

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):	
	if not message.author.bot and message.content.split()[0] == '!reservoir':
		log('discord-info', message.content)
		await message.channel.send('Let me consult our documentation and get right back to you. Just a moment please.')
		question = ' '.join(message.content.split()[1:])
		await message.channel.send(answerQuestion(question))					

client.run(DISCORD_TOKEN)

