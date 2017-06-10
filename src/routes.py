from flask import request, redirect, flash, url_for
from pprint import pformat, pprint
from main import *
import validators


@app.route("/<short_url>", methods=['GET', 'POST'])
def retrieve(short_url):
    if short_url is None or short_url == 'favicon.ico':
        return redirect(url_for("index"))

    if short_url_exists(short_url):
        shortening = get_shortening(short_url=short_url)
        shortening += 1

        return redirect(shortening.long_url, code=302)
    else:
        flash('{} is not mapped to any URL.'.format(
            request.url_root + short_url))
        return redirect(url_for("index"))


@app.route("/", methods=['GET', 'POST'])
def index():
    data = {
        'number_of_urls': get_number_of_shortenings(),
        'remote_address': get_remote_address(),
        'debug': app.config['DEBUG'],
    }

    if request.method == 'POST':
        data.update({
            'protocol': request.form['protocol'],
            'long_url_without_protocol': request.form['url'],
            'base_url': request.url_root,
            'wants_custom': request.form['wants_custom'],
            'custom_url': request.form['custom_url'],
        })

        data['long_url'] = data['protocol'] + data['long_url_without_protocol']

        if not validators.url(data['long_url'], public=True):
            flash("%s is not a valid URL." % data['long_url'])
            print("%s is not a valid URL." % data['long_url'])
            return redirect(url_for('index'))

        if data['wants_custom'] == 'yes':
            if not validate_short_url(data['custom_url']):
                flash("%s is not a valid custom URL." % data['custom_url'])
                print("%s is not a valid custom URL." % data['custom_url'])
                return redirect(url_for('index'))

            if short_url_exists(data['custom_url']):
                if get_long_url(data['custom_url']) != data['long_url']:
                    flash("Short URL is already mapped to something else!")
                    return redirect(url_for('index'))
                else:
                    data['short_url'] = data['custom_url']
                    return render_template("index.html", data=data)

            try:
                shorten(data['long_url'], data['custom_url'])
                data['short_url'] = data['custom_url']
            except Exception as e:
                flash("Could not shorten %s to %s. Reason: %s" % \
                        (data['long_url'], data['custom_url'], e))
                return redirect(url_for('index'))

        else:
            if not long_url_exists(data['long_url']):
                try:
                    shorten(data['long_url'])
                except Exception as e:
                    flash("Could not shorten %s. Reason: %s" % e)
                    return redirect(url_for('index'))
            data['short_url'] = get_short_url(data['long_url'])


    pretty_data = pformat(data, indent=2).replace("\n", "<br>")
    print(pretty_data)

    return render_template("index.html", data=data, pretty_data=pretty_data)


@app.route("/all")
def show_all():
    return render_template("all.html",
                           shortenings=get_all_shortenings(),
                           url_root=request.url_root)


@app.errorhandler(404)
def page_not_found(error):
    return "page not found"
