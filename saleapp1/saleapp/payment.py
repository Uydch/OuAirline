import json
import os
import random
from saleapp import app
from payos import PaymentData, ItemData, type,PayOS
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from dotenv import load_dotenv,dotenv_values

load_dotenv()

client_id = os.getenv('PAYOS_CLIENT_ID')
api_key = os.getenv('PAYOS_API_KEY')
checksum_key = os.getenv('PAYOS_CHECKSUM_KEY')
payOS = PayOS(client_id=client_id, api_key=api_key, checksum_key=checksum_key)

def create_payment(amount):
    domain = "http://127.0.0.1:5000"
    try:
        paymentData = PaymentData(orderCode=random.randint(1000000,9999999),amount=amount,description="demo",
                                  cancelUrl=f"{domain}/cancel",returnUrl=f"{domain}/success")
        payosCreatePayment = payOS.createPaymentLink(paymentData)
        return payosCreatePayment.to_json()
    except Exception as e:
        return jsonify(error=str(e)),403



