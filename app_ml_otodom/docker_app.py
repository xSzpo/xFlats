from flask import Flask, request, jsonify
from sklearn.externals import joblib
import pandas as pd
import numpy as np
import json
import random
import os
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    json_ = json.loads(request.data)
    df = pd.DataFrame(json_)
    np.random.seed(666)
    random.seed(666)
    os.environ['PYTHONHASHSEED'] = str(666)
    prediction = clf.predict(df)
    prediction = np.expm1(prediction)
    return jsonify({'prediction': list(prediction)})


if __name__ == '__main__':
    clf = joblib.load('model.pkl')
    print("zaladowano model")
    app.run(host='0.0.0.0', port=8080, debug=True)

