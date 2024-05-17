import pandas as pd
import os#
import matplotlib.pyplot as plt
import time
import redis
from flask import Flask, render_template, url_for

app = Flask(__name__)
cache = redis.Redis(host='srv-captain--redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

# Route for Titanic page
@app.route('/titanic')
def titanic():
    # Load Titanic data from CSV using pandas
    df = pd.read_csv('titanic.csv')

# Calculate the number of survivors based on gender
    gender_survivors = df[df['survived'] == 1].groupby('sex').size()

    # Generate the bar chart
    plt.figure(figsize=(8, 6))
    gender_survivors.plot(kind='bar', color=['skyblue', 'lightgreen'])
    plt.title('Survivors by Gender')
    plt.xlabel('Gender')
    plt.ylabel('Number of Survivors')
    plt.xticks(rotation=0)
    
    # Save the bar chart as an image
    chart_path = os.path.join(app.static_folder, 'survivors_chart.png')
    plt.savefig(chart_path)
    plt.close()

    # Convert the first 5 rows of DataFrame to HTML format
    table_html = df.head().to_html()

    # Pass the HTML table and chart path to titanic.html template
    return render_template('titanic.html', table=table_html, chart_path='survivors_chart.png')

# Here static image file
@app.route('/static/hwr_logo.png')
def serve_image():
    return app.send_static_file('hwr_logo.png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)