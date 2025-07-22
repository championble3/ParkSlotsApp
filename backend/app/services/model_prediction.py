import torch
import joblib
import numpy as np
from app.services.model import RegressionModel

model = RegressionModel(input_size=7)
model.load_state_dict(torch.load('models/park_slots_pred_model.pth'))
model.eval()

x_scaler = joblib.load('models/x_scaler.pkl')
y_scaler = joblib.load('models/y_scaler.pkl')

def predict_slots(single_input_row):
    input_array = np.array(single_input_row).reshape(1, -1).astype('float32')
    input_scaled = x_scaler.transform(input_array)
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32)

    with torch.no_grad():
        prediction = model(input_tensor)
    prediction_unscaled = y_scaler.inverse_transform(prediction.numpy())
    value = int(round(prediction_unscaled[0][0]))
    return max(value, 0)
