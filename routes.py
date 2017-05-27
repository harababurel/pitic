from flask import request, redirect, flash, url_for
from main import *


@app.route("/<short_url>", methods=['GET', 'POST'])
def retrieve(short_url):
    if short_url_exists(short_url):
        long_url = get_long_url(short_url)
        return redirect(long_url, code=302)
    else:
        flash('{} is not mapped to any URL.'.format(
            request.url_root + short_url))
        return redirect(url_for("index"))


@app.route("/", methods=['GET', 'POST'])
def index():
    data = None
    if request.method == 'POST':
        protocol = request.form['protocol']
        long_url_without_protocol = request.form['url']
        long_url = protocol + long_url_without_protocol
        base_url = request.url_root

        if not long_url_exists(long_url):
            try:
                shorten(long_url)
            except Exception as e:
                return 'could not shorten <samp>%s</samp>: %s' % (long_url, e)

        data = {
            'protocol': protocol,
            'long_url_without_protocol': long_url_without_protocol,
            'long_url': long_url,
            'short_url': get_short_url(long_url),
            'base_url': base_url,
        }

    return render_template("index.html", data=data)


@app.route("/all")
def show_all():
    return render_template("all.html", entries=get_all_entries())


@app.errorhandler(404)
def page_not_found(error):
    return "page not found"
