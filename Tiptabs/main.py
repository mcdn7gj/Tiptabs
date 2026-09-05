#!/usr/bin/env python3

import os
import sys
import logging
import requests
from pathlib import Path
from Tiptabs.Tiptabs import *
from dotenv import load_dotenv
from Tiptabs.TiptabsDB import *
from Tiptabs.PhoneVerifier import *
from os.path import dirname, abspath
from Tiptabs.DictionaryBuilder import *
from flask import Flask, render_template, request, jsonify, make_response

def main():
    """
    main() - Main class for Tiptabs. The Flask web application is created in this file.
    Additionally, this file handles the creation of the dictionary of currencies.
    """
    
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    env_path = str(Path(dirname(dirname(abspath(__file__)))) / '.env')
    logger.debug("Loading .env file from: {!s}".format(env_path))    
    load_dotenv(dotenv_path=env_path)

# APP_PORT = int(os.getenv("APP_PORT"))
#     logger.debug("Chosen port for application: {!s}".format(str(APP_PORT)))

#     APP_ADDRESS = str(os.getenv("APP_HOST"))
#     logger.debug("Chosen address for application: {!s}".format(APP_ADDRESS))

#     phone_verifier = PhoneVerifier(str(os.getenv("SMS_FORMAT")), str(os.getenv("SMS_COUNTRY_CODE")), str(os.getenv("SMS_URL")), str(os.getenv("SMS_KEY")))

#     logger.debug("Rates Service being requested from: {!s}".format(str(os.getenv("RATES_URL"))))

    dictionary_builder = DictionaryBuilder()
#     logger.debug("DictionaryBuilder created.")

#     logger.info("Check availability of Rates API. ({!s})".format(str(os.getenv("RATES_URL"))))
    exec_rates = dictionary_builder.request_rates(str(os.getenv("RATES_URL")), str(os.getenv("RATES_KEY")), str(os.getenv("RATES_FORMAT")))

    if not exec_rates[0]:
        logger.info(str(exec_rates[1]))
        FROM_ADDRESS = str(os.getenv("FROM_ADDRESS"))
        TO_ADDRESS = str(os.getenv("TO_ADDRESS"))
        GMAIL_PW = str(os.getenv("GMAIL_PW"))
        dictionary_builder.send_error_message(FROM_ADDRESS, TO_ADDRESS, GMAIL_PW)
    #return make_response(jsonify({'False': 'Rates service not available.'}))

    populate_dictionary_result = dictionary_builder.get_rates(exec_rates[0], exec_rates[1])

    tiptabs_core = Tiptabs(str(os.getenv("STARTING_RATE")), dictionary_builder)
#     logger.info("Initialize Tiptabs core with base rate: {!s} ...".format(str(os.getenv("STARTING_RATE"))))
    
    rates = list(dictionary_builder.currencies.keys())
#     logger.info("-- {!s} conversion rates succesfully recieved!".format(len(rates)))

    rates.sort()
#     logger.info("-- Sorting {!s} rates in alphanumeric order ...".format(len(rates)))

#     logger.info(" Initializing Flask application ...")

#     @app.route('/result', methods=['POST'])
#     def send_sms(desired_number):        
#         valid_number = phone_verifier.verifyPhone(desired_number)        
#         if valid_number:
#             phone_verifier.send_sms_to_number(desired_number)

#     @app.route('/fixer_status', methods=['GET'])
#     def get_fixer_status():
#         fxr_resp = [False, "Fixer.io is not available."]
#         if request.method == 'GET':
#             if exec_rates:
#                 fxr_resp = [exec_rates, "Fixer.io is available for use."]
#         return render_template("fixer_status.html", resp=fxr_resp[0], result=fxr_resp[1])

#     @app.route('/feedback', methods=['GET', 'POST'])
#     def send_feedback():
#         return render_template("feedback.html")

#     @app.errorhandler(404)
#     def no_page_found(e):
#         return render_template('error_404.html')

    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'service': 'Tiptabs'}), 200
    
    @app.route('/', methods=['GET', 'POST', 'PUT'])
    def home():
        if request.method == 'GET':
            return render_template("app.html", rates=rates)
        elif request.method == 'POST':
            post_form_resp = [False, "ERROR: Request form was invalid/empty."]
            if request.form:
                base = str(request.form['base_currency'])
                check_avail_base = dictionary_builder.check_available_bases(base)
                if not check_avail_base:
                    base_not_avail_resp = 'ERROR: Chosen base "{!s}" is not available.'.format(base)
                    return jsonify({str(False): str(base_not_avail_resp)})
                
                total_bill_amount = str(request.form['bill_amount'])
                total_tip_percentage = str(request.form['tip_percentage'])
                total_desr_currency = str(request.form['converted_currency'])

                # Set the internal base to desired rate.
                # set_base_result = tiptabs_core.set_base(total_base_currency)

                check_desr_currency = dictionary_builder.check_available_bases(total_desr_currency)
                post_form_resp = tiptabs_core.calculate_total(total_bill_amount, total_tip_percentage, total_desr_currency)
                return jsonify({str(post_form_resp[0]): str(post_form_resp[1])})


    @app.errorhandler(404)
    def no_page_found(e):
        return make_response(jsonify({'ERROR': 'Not Found.'}), 404)


    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
