try:
    from flask.ext.cors import CORS
    from flask import Flask
    import pandas as pd
    import json
except ImportError as error:
    print error
    print '\nPlease run this command resolve this error :'
    print '\tpip install flask flask-cors pandas'
    sys.exit()



APP = Flask(__name__)
VARS = {}

def prepare_data():
    data = pd.read_csv('all_earthquakes.csv', low_memory=False)
    data['year'] = data['time'].apply(lambda x: x[:4])
    VARS['data'] = data
    return True

prepare_data()

@APP.route('/earthquakes', methods=['GET'])
def earthquakes_by_year():
    """Return The trend per year"""
    data = VARS['data']
    grouped = data.groupby('year')
    count = grouped['mag'].count()
    return count.to_csv(None, index=False)


@APP.route('/earthquakes/<year>', methods=['GET'])
def earthquakes_in_year(year='2015'):
    """Filter the dataset by year and return in csv format"""
    data = VARS['data']
    filtered_data = data[data['year'] == year]
    return filtered_data.to_csv(None, index=False)


@APP.route('/', methods=['GET'])
def dashboard():
    """Return the HTML for the dashboard"""
    return None


if __name__ == "__main__":
    CORS(APP)
    APP.run(debug=True)
