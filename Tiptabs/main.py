#!/usr/bin/env python3

import logging
import os
from os.path import abspath, dirname
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, render_template, request

from Tiptabs.ForexCache import ForexCache
from Tiptabs.ForexConfig import ForexConfig
from Tiptabs.ForexRefresh import ForexRefresh
from Tiptabs.ForexService import ForexService
from Tiptabs.FrankfurterProvider import FrankfurterProvider
from Tiptabs.Tiptabs import Tiptabs


def create_app(forex_service, tiptabs_core=None, rates=None):
    app = Flask(__name__)
    rates = sorted(rates or _available_currencies(forex_service))
    tiptabs_core = tiptabs_core or Tiptabs("EUR", forex_service=forex_service)

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'Tiptabs'}), 200

    @app.route('/', methods=['GET', 'POST', 'PUT'])
    def home():
        if request.method == 'GET':
            return render_template("app.html", rates=rates)
        if request.method == 'POST' and request.form:
            base = str(request.form.get('base_currency', ''))
            if not tiptabs_core.set_base(base)[0]:
                return jsonify({'False': 'ERROR: Chosen base "{!s}" is not available.'.format(base)})

            result = tiptabs_core.calculate_total(
                request.form.get('bill_amount'),
                request.form.get('tip_percentage'),
                request.form.get('converted_currency'),
            )
            return jsonify({str(result[0]): str(result[1])})
        return jsonify({'False': 'ERROR: Request form was invalid/empty.'})

    @app.errorhandler(404)
    def no_page_found(error):
        return make_response(jsonify({'ERROR': 'Not Found.'}), 404)

    return app


def _available_currencies(forex_service):
    currencies = set()
    for key in forex_service.available_pairs():
        currencies.update(key.split('/'))
    return currencies


def _configured_currencies(provider_pairs):
    currencies = set()
    for pair in provider_pairs:
        currencies.update(pair.replace('/', '-').split('-'))
    return currencies


def main():
    """
    main() - Start the Flask application and its internal forex provider lifecycle.
    """

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    env_path = str(Path(dirname(dirname(abspath(__file__)))) / '.env')
    logger.debug("Loading .env file from: {!s}".format(env_path))
    load_dotenv(dotenv_path=env_path)

    config = ForexConfig.from_env()
    cache = ForexCache()
    forex_service = ForexService(cache, freshness_seconds=config.freshness_seconds)
    tiptabs_core = Tiptabs(os.getenv("STARTING_RATE", "EUR"), forex_service=forex_service)
    provider = FrankfurterProvider(config, cache.put, logger=logger)
    refresh = ForexRefresh(provider, forex_service, config.refresh_seconds, logger=logger)
    refresh.start()
    app = create_app(
        forex_service,
        tiptabs_core=tiptabs_core,
        rates=_configured_currencies(config.pairs),
    )
    logger.info("Forex service configured for pairs: %s", ", ".join(config.pairs))
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        refresh.stop()


if __name__ == '__main__':
    main()
