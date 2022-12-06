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
    
    #function to append lock to the blockchain
    def append_block(self, n, last_sale_hash):
        newBlock = {
            'index': len(self.ledger),
            'transactions': self.recent_cars_sold,
            'nonce': n,
            'last_sale_hash': last_sale_hash
        }
        self.recent_cars_sold = []
        self.ledger.append(newBlock)
        return newBlock

    #function for sale, give values for all the fields
    def sale_add(self, accidents, modifications, condition, mileage, vin, cost, seller, buyer):
        self.recent_cars_sold.append({
            'accidents': accidents,
            'modifications': modifications,
            'condition': condition,
            'mileage': mileage,
            'vin': vin,
            'cost': cost,
            'seller': seller,
            'buyer': buyer
        })
        #makes all car sales global and all the fields below it
        global all_car_sales
        all_car_sales.append({
            'accidents': accidents,
            'modifications': modifications,
            'condition': condition,
            'mileage': mileage,
            'vin': vin,
            'cost': cost,
            'seller': seller,
            'buyer': buyer
        })
        return self.last_block['index'] + 1

    #proerty gives special functions for post and get
    @property
    def last_block(self):
        return self.ledger[-1]

#Creating an app for using postman as the gui
app = Flask(__name__)
CV = carVerifications()

#overview to see the history of the car and other transactions made
@app.route('/CarHistory', methods=['GET'])
#contains all transactions made currently but not in the past
def full_ledger():
    response = {
        'ledger': CV.ledger,
        'length': len(CV.ledger)
    }
    return jsonify(response), 200

#new transactions that are currently made. It will allow the individual to enter specifics of a car that a customer needs to know before buying.
@app.route('/carSale/new', methods=['POST'])
def sales_new():
    values = request.get_json()
    required_fields = ['accidents', 'modifications', 'condition', 'mileage', 'vin', 'cost', 'seller', 'buyer']
    if not all(k in values for k in required_fields):
        return ('Missing Fields', 400)
    index = CV.sale_add(
        values['accidents'],
        values['modifications'],
        values['condition'],
        values['mileage'],
        values['vin'],
        values['cost'],
        values['seller'],
        values['buyer']
    )
    response = {'message': f'Transaction completed. It will show when the newCar is sold/mined {index}'}
    return (jsonify(response), 201)

#overview to see the history of the car and other transactions made
@app.route('/CarHistory', methods=['GET'])
#contains all transactions made currently but not in the past
def full_ledger():
    response = {
        'ledger': CV.ledger,
        'length': len(CV.ledger)
    }
    return jsonify(response), 200


#This function will get all of the information from the transactions (which include accidents, modifications, mileage, etc) made and create a new block for that transaction
@app.route('/newCar', methods=['GET'])
def car_block():
    CV.sale_add(
        accidents=0,
        modifications="0",
        condition="0",
        mileage=0,
        vin="CA1MS37A0PW123456",
        cost=0,
        seller="unknown",
        buyer="unknown"
    )
    last_block_hash = CV.hash_of_block(CV.last_block)
    index = len(CV.ledger)
    n = CV.Proof_of_Work(index, last_block_hash, CV.recent_cars_sold)
    block = CV.append_block(n, last_block_hash)
    response = {
        'message': "New block has been mined for the recent car purchase",
        'index': block['index'],
        'hash_of_last_sale': block['last_sale_hash'],
        'nonce': block['nonce'],
        'transaction': block['transactions']
    }
    return jsonify(response), 200

#This function allows the customer to see all of the past transactions (which include accidents, modifications, mileage, etc) that have been made for the car before buying it. 
@app.route('/allCarSales', methods=['GET'])
def car_sales():
    global all_car_sales
    response = all_car_sales
    return (jsonify(response), 201)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
