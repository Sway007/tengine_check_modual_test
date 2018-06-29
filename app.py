import argparse

from flask import Flask


parser = argparse.ArgumentParser()
parser.add_argument('--noden', '-n', help='specify the server node number')
args = parser.parse_args()


app = Flask(__name__)

@app.route('/')
def hello():
    return 'hello from node {}'.format(args.noden)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=80)