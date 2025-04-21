from flask import Flask, render_template, request
import requests
import json
import csv
# pythonanywhere link: https://rkprashad.pythonanywhere.com/

# gitHub public APIs > News > https://newsapi.org/
api_key = 'pub_684944c54bb6dae688208ee2a0304228081a5'
url = f"https://newsdata.io/api/1/latest?apikey={api_key}"
# r=requests.get(url)
# r.status_code
# r.json()
# r.json()['results']
# r.json()['results'][0] = article Id
# API Documentation > https://newsdata.io/documentation
# need to filter data by language and country

""" 
sudo code
func to filter data by country and language (+keyword and category) -- index.html
 - parameters country and language - can be keep these as default
 - to add search keyword and category -- initialise to None
 - from api documentation parameter 'q' for keyword search, parameter 'category' to filter by category
 - find a way to pass parameters
 func to return article = r.json()['results'][0] to extract a specific article -- show.html
 - straight forward function. just need to find a way to pass the parameter 'article_id'
 - use the article_id to show the specific data
"""

# Function to filter country to Australia, Language to English and if keyword and category is/are entered/true then filter by them as well.
def news_articles(keyword=None, category=None, country='au', language='en'):
    # https://stackoverflow.com/questions/50737866/python-requests-pass-parameter-via-get
    payload = {
        'country': country,
        'language': language,
    }
    # search form to be used in index.html
    if keyword:
        payload['q'] = keyword  # https://newsdata.io/documentation > 'q' is to search keywords
    if category:
        payload['category'] = category
    #
    r = requests.get(url, params=payload)
    if r.status_code == 200:
        return r.json()['results']
    else:
        print(f"Something went wrong, News not available : {r.status_code}")
        return []


# Function to extract the article using article Id
def article_by_id(article_id):
    payload = {
        'id': article_id,
    }
    r = requests.get(url, params=payload)
    if r.status_code == 200:
        return r.json()['results'][0]  # =article
    else:
        print(f"Request was not successful: {r.status_code}")
        return None


# display current weather of the visitor location
def get_user_weather():
    # from githup public apis > Geocoding > Abstract IP Geolocation > https://www.abstractapi.com/api/ip-geolocation-api
    api_key1 = '3fb93eca12934057ae39808ae97618e6'
    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={api_key1}&ip_address="
    res1=requests.get(url)
    # this returns a byte array. so we need to convert it to json dictionary
    # https://stackoverflow.com/questions/40059654/convert-a-bytes-array-into-json-format
    my_bytes_value =res1.content
    my_json = my_bytes_value.decode('utf8').replace("'", '"')
    visitor_location = json.loads(my_json)
    lat = visitor_location['latitude'] 
    lon = visitor_location['longitude']
    # from weather app class notes
    api_key2 = '945adbb603b4fda2f19f4fa7a6b88699'
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key2}&units=metric"
    try:
        res2=requests.get(url)
        assert res2.status_code == 200
        return [res2.json()['main']['temp'],res2.json()['weather'][0]['description'], res2.json()['main']['feels_like'], res2.json()['main']['humidity'], \
                res2.json()['main']['temp_min'],res2.json()['main']['temp_max'],visitor_location['city'], visitor_location['region'],visitor_location['country']]
    except AssertionError:
        print("Something went wrong")
        return None
    
# End display current weather    

# Forex
def exch_rates():
    api_key3 = '913444f7c03dd71b6dc4c7aa'
    url = f"https://v6.exchangerate-api.com/v6/{api_key3}/latest/AUD"
    try:
        res3=requests.get(url)
        assert res3.status_code == 200
        return [res3.json()['conversion_rates']['USD'], res3.json()['conversion_rates']['NZD'], res3.json()['conversion_rates']['CNY'], \
                res3.json()['conversion_rates']['JPY'], res3.json()['conversion_rates']['EUR']]             
    except AssertionError:
        print("Something went wrong")
        return None


# Flast App
app = Flask(__name__)


# index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    # https://stackoverflow.com/questions/11774265/how-do-you-access-the-query-string-in-flask-routes
    # https://flask.palletsprojects.com/en/stable/api/#flask.Request.args
    keyword = request.args.get('keyword', '') # get dictionay of values for keyword
    category = request.args.get('category', '') # get dictionay of values for category
    articles = news_articles(keyword=keyword, category=category)
    weather = get_user_weather()
    exchange_rates = exch_rates()
    return render_template('index.html', articles=articles, keyword=keyword, category=category, weather=weather, exchange_rates=exchange_rates)


#save email addresses to csv (from Lesson 18 forms video)
@app.route('/data', methods=['GET','POST'])
def save_email():
    email = request.form.get('email')   # https://stackoverflow.com/questions/13279399/how-to-obtain-values-of-request-variables-using-python-and-flask
    with open('data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([email])  
    return render_template('data.html', email=email)  

           
# show.html
@app.route('/article/<article_id>', methods=['GET'])
def show_article(article_id):
    article = article_by_id(article_id)
    if article:
        return render_template('show.html', article=article)
    else:
        return "Article not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
