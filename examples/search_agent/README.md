# Search Agent
This example demonstrates how to build a simple search agent that uses the [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework). **The most important part of the example is the `search_agent.py` file, which demonstrates how to subclass the `AbstractAgent` class, implement the `assist` method, and create and serve Sentient Chat events.**

## Running the search agent
> [!NOTE]
> **These instructions are for unix-based systems (i.e. MacOS, Linux). Before you proceed, make sure that you have installed `python` and `pip`. If you have not, follow [these](https://packaging.python.org/en/latest/tutorials/installing-packages/) instructions to do so.**

#### 1. Create secrets file
Create the `.env` file by copying the contents of `.env.example`. This is where you will store all of your agent's credentials.
```
cp .env.example .env
```

#### 2. Add model credentials
Add your Fireworks API key to the `.env` file (you can also use any other OpenAI compatible inference provider).

#### 3. Add search provider credentials
Add your Tavily API key to the `.env` file.

#### 4. Create Python virtual environment:
```
python3 -m venv .venv
```

#### 5. Activate Python virtual environment:
```
source .venv/bin/activate
```

#### 6. Install dependencies:
```
pip install -r requirements.txt
```

#### 7. Run the search agent:
```
python3 -m src.search_agent.search_agent
```

#### 8. Use a tool like [CuRL](https://curl.se/) or [Postman](https://www.postman.com/) to query the server. The agent exposes a single `assist` endpoint:
```
curl -N --location 'http://0.0.0.0:8000/assist' \
--header 'Content-Type: application/json' \
--data '{
    "query": {
        "id": "01JQETZTSNT4KC0TRS6EBN32TG",
        "prompt": "Who is Lionel Messi?"
    },
    "session" : {
        "processor_id": "Example processor ID",
        "activity_id": "01JR8SXE9B92YDKKNMYHYFZY1T",
        "request_id": "01JR8SY5PHB9X2FET1QRXGZW76",
        "interactions": []
    }
}'
```
Expected output:
```
event: SEARCH
data: content_type=<EventContentType.TEXTBLOCK: 'atomic.textblock'> event_name='SEARCH' schema_version='1.0' id=ULID(01JRK1GY08KR591483SMED2F5B) source='Example processor ID' metadata=None content='Searching internet for results...'

event: SOURCES
data: content_type=<EventContentType.JSON: 'atomic.json'> event_name='SOURCES' schema_version='1.0' id=ULID(01JRK1H0JHE89BGT8WJWFCF0FM) source='Example processor ID' metadata=None content={'results': [{'title': "Lionel Messi | Biography, Trophies, Records, Ballon d'Or, Inter Miami ...", 'url': 'https://www.britannica.com/biography/Lionel-Messi', 'content': 'Lionel Messi is an Argentine-born football (soccer) player who has been named the world’s best men’s player of the year seven times (2009–12, 2015, 2019, and 2021). In 2022 he helped Argentina win the World Cup. Naturally left-footed, quick, and precise in control of the ball, Messi is known as a keen pass distributor and can readily thread his way through packed defenses. He led Argentina’s national team to win the 2021 Copa América and the 2022 World Cup, when he again won the Golden Ball award.', 'score': 0.9152729, 'raw_content': None}, {'title': 'Lionel Messi: Biography, Soccer Player, Inter Miami CF, Athlete', 'url': 'https://www.biography.com/athletes/lionel-messi', 'content': 'Lionel Messi: Biography, Soccer Player, Inter Miami CF, Athlete Search Black History Month History & Culture Movies & TV Musicians Athletes Artists Power & Politics Business Scholars & Educators Scientists Activists Notorious Figures BIO Buys Newsletter Your Privacy Choices Privacy NoticeTerms Of Use Skip to Content Black History Month Musicians Movies & TV History & Culture Newsletter Kendrick Lamar The Real Belle Gibson Gisele Bündchen Joe Rogan A Black History Pioneer Famous Athletes Lionel Messi Lionel Messi Lionel Messi, a forward for Inter Miami CF, is one of the world’s greatest soccer players and helped the Argentina national team win its third FIFA World Cup in 2022. The four-part series promises the most personal interviews to date with Messi and “an intimate and unprecedented look at his quest for a legacy-defining World Cup victory.” View full post on Youtube Messi, now playing for Inter Miami CF of the MLS, helped his home country win soccer’s biggest event for the first time since 1986, scoring two goals in the final and leading Argentina to a 4-2 win over Kylian Mbappé and France on penalties. Lionel Messi is an Argentinian soccer player who has played for FC Barcelona, Paris Saint-Germain, and currently, the MLS club Inter Miami CF as well as the Argentina national team. In 2012, he set a record for most goals in a calendar year and, a decade later, helped the Argentina national team win its third FIFA World Cup.', 'score': 0.90965873, 'raw_content': None}, {'title': 'Lionel Messi - Wikipedia', 'url': 'https://en.wikipedia.org/wiki/Lionel_Messi', 'content': "Widely regarded as one of the greatest players of all time, Messi set numerous records for individual accolades won throughout his professional footballing career such as eight Ballon d'Or awards and eight times being named the world's best player by FIFA.[note 2] He is the most decorated player in the history of professional football having won 45 team trophies,[note 3] including twelve Big Five league titles, four UEFA Champions Leagues, two Copa Américas, and one FIFA World Cup. Messi holds the records for most European Golden Shoes (6), most goals in a calendar year (91), most goals for a single club (672, with Barcelona), most goals (474), hat-tricks (36) and assists (192) in La Liga, most assists (18) and goal contributions (32) in the Copa América, most goal contributions (21) in the World Cup, most international appearances (191) and international goals (112) by a South American male, and the second-most in the latter category outright.", 'score': 0.846159, 'raw_content': None}, {'title': '50 Facts About Lionel Messi', 'url': 'https://facts.net/lifestyle/sports/50-facts-about-lionel-messi/', 'content': "Everything Else Facts Everything Else Facts 50 Facts About Lionel Messi 08Early Success: Within three years of his debut, Messi established himself as an integral player for FC Barcelona, helping the team achieve numerous titles and setting records that would be hard to break. 13La Liga Titles: Messi has won ten La Liga titles with FC Barcelona, making him one of the most successful players in the league's history. 17Club Goals: Messi has scored over 850 senior career goals for club and country, making him one of the highest-scoring players in football history. 47FIFA Club World Cup Wins: Messi has won one FIFA Club World Cup title with FC Barcelona, demonstrating his team's global success. More Facts", 'score': 0.5515985, 'raw_content': None}, {'title': 'Official site', 'url': 'https://messi.com', 'content': 'Lionel Messi', 'score': 0.46089602, 'raw_content': None}]}

event: FINAL_RESPONSE
data: content_type=<EventContentType.TEXT_STREAM: 'chunked.text'> event_name='FINAL_RESPONSE' schema_version='1.0' id=ULID(01JRK1H185GPX4GM5AX3WMCKKM) source='Example processor ID' metadata=None stream_id='sl2ou800n2' is_complete=False content='Lion'

...

event: done
data: content_type=<EventContentType.DONE: 'atomic.done'> event_name='done' schema_version='1.0' id=ULID(01JRK1H4EZ8F51REBCWAR391MM) source='Example processor ID' metadata=None

```