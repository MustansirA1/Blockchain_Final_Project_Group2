#python imports used
import hashlib
import json
from flask import Flask
from flask.globals import request
from flask.json import jsonify
from urllib.parse import urlparse

#empty list that will be used to display all car sales, even from the past (if entered in our application)
all_car_sales = []

#class for car verification
class carVerifications(object):
    #secure level set to 00 for the purpose of this project
    hash_secure_level = "00"
    def __init__(self):
        #empty list for ledger
        self.ledger = []
        #empty list for recent cars sold
        self.recent_cars_sold = []
        first_block_hash = self.hash_of_block("First mined block")
        #append block
        self.append_block(
            last_sale_hash=first_block_hash,
            n=self.Proof_of_Work(0, first_block_hash, [])
        )
    #function for block that returns hashed
    def hash_of_block(self, block):
        encoder = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha512(encoder).hexdigest()

    #function for proof of work, adds 1 if validate is false
    def Proof_of_Work(self, index, last_sale_hash, car_sales):
        n = 0
        while self.validate_Proof(index, last_sale_hash, car_sales, n) is False:
            n += 1
            print(n)
        print(n)
        return n

    #function for validate, returs a newhash with the added security level
    def validate_Proof(self, index, last_sale_hash, car_sales, n):
        newData = f'{index},{last_sale_hash},{car_sales},{n}'.encode()
        newHash = hashlib.sha512(newData).hexdigest()
        return newHash[:len(self.hash_secure_level)] == self.hash_secure_level
