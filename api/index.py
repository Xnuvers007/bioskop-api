from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bioskop API</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }

            h1 {
                color: #007BFF;
            }

            p {
                font-size: 1.2rem;
                margin-bottom: 20px;
            }

            a {
                display: inline-block;
                padding: 10px 20px;
                background-color: #007BFF;
                color: #fff;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s ease;
            }

            a:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to Bioskop API</h1>
        <p>Visit the Bioskop endpoint by clicking the link below:</p>
        <a id="bioskopLink" href="#">Go to Bioskop</a>

        <script>
            document.getElementById("bioskopLink").addEventListener("click", function() {
                alert("You clicked the Bioskop link! Add your custom JavaScript actions here.");
                window.location.href = "/bioskop?search=";
            });
        </script>
    </body>
    </html>
    """

    return html_content, 200


def scrape_bioskop(base_url, search_term, pages=1):
    complete = f"?s={search_term}&post_type%5B%5D=post&post_type%5B%5D=tv"
    results = []

    for page in range(1, pages + 1):
        full_url = f"{base_url}page/{page}/{complete}"
        try:
            r = requests.get(full_url, headers={
                             'User-Agent': 'Mozilla/5.0'})

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                entries = soup.find_all(
                    'div', class_='content-thumbnail text-center')
                title = soup.find_all(
                    'h2', class_='entry-title', itemprop='headline')

                for entry, judul in zip(entries, title):
                    a_tag = judul.find('a')
                    if a_tag:
                        judulbioskop = a_tag.get_text(strip=True)

                    title_tag = entry.find('a', itemprop='url')
                    if title_tag:
                        href = title_tag.get('href')
                        title = title_tag.get_text(strip=True)
                        img_tag = entry.find('img', itemprop='image')
                        if img_tag:
                            img_src = img_tag.get('src')
                            result = {
                                "URL": full_url,
                                "Title": judulbioskop,
                                "Href": href,
                                "Img": img_src
                            }
                            results.append(result)
            else:
                pass
        except requests.exceptions.ReadTimeout:
            jsonify({"error": "ReadTimeout"}), 408
            continue  # Skip this iteration and proceed to the next
        except requests.exceptions.RequestException:
            jsonify({"error": "Please turn on internet connection"}), 500

    return results


def scrape_other_url(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        films = soup.find_all('div', class_='ml-item')
        results = []

        for film in films:
            result = {
                "Title": film.find('img')['alt'],
                "Info": film.find('span', class_='mli-info').text,
                "Rating": film.find('span', class_='mli-rating').text,
                "Href": film.find('a')['href'],
                "Img": film.find('img')['src']
            }
            results.append(result)

    except requests.exceptions.ReadTimeout:
        jsonify({"error": "ReadTimeout"}), 408
    except requests.exceptions.RequestException:
        jsonify({"error": "Please turn on internet connection"}), 500

    return results


@app.route('/bioskop', methods=['GET'])
def bioskop():
    search_term = request.args.get('search')
    if not search_term:
        return jsonify({"error": "Search term is required",
                        "path": request.host_url + 'bioskop?search=naruto'
                        }), 200

    base_urls = [
        'http://109.123.251.95/',
        'https://165.232.85.56/',
        'http://154.26.134.91/',
        'https://45.148.122.77/',
        'http://161.97.104.222/',
        'http://213.136.74.97/',
        'http://157.230.241.72/',
        'http://5.189.159.251/',
        'http://157.230.241.72/',
        'http://207.180.208.171/',
        'http://164.68.127.236/',
        'http://5.189.157.70/',
        'http://5.189.170.137/',
        'https://185.99.135.217/',
        'http://173.212.248.78/'
        'http://5.189.173.193/'
    ]

    bioskop_results = []
    for base_url in base_urls:
        bioskop_results.extend(scrape_bioskop(base_url, search_term))

    other_url = f"http://179.43.163.54/?s={search_term}"
    other_results = scrape_other_url(other_url)

    return jsonify({"bioskop": bioskop_results, "other": other_results})


if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0')
