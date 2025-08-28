import requests 
import json 
import pandas as pd 
from datetime import datetime, timedelta 
import pyodbc
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import random 
import joblib
import os

server = 'TOMASZ' 
database = 'pwr_park_db'
user = 'tomek' 
password = '063900'
driver='ODBC Driver 17 for SQL Server'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password}'

conn = pyodbc.connect(connection_string)

sql_query = f"""SELECT * FROM park_table"""
df = pd.read_sql_query(sql_query,conn)
conn.close()

df['time_park'] = pd.to_datetime(df['time_park'], format='%H:%M')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
df['Year'] = df['date'].dt.year
df['Month'] = df['date'].dt.month
df['Day'] = df['date'].dt.day
df['Weekday'] = df['date'].dt.weekday
df['Hour'] = df['time_park'].dt.hour
df['Minute'] = df['time_park'].dt.minute
df = df.drop(columns=['time_park', 'date'])

X = df[['park_id','Year','Month','Day','Weekday','Hour','Minute']].values.astype('float32')
y = df['park_slots'].values.astype('float32').reshape(-1, 1)

x_scaler = StandardScaler()
y_scaler = StandardScaler()

X = x_scaler.fit_transform(X)
y = y_scaler.fit_transform(y)

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 
model_dir = os.path.join(BASE_DIR, "models")

joblib.dump(x_scaler, os.path.join(model_dir, 'x_scaler.pkl'))
joblib.dump(y_scaler, os.path.join(model_dir, 'y_scaler.pkl'))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32)

class RegressionModel(nn.Module):
    def __init__(self, input_size):
        super(RegressionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.fc2 = nn.Linear(128, 64)
        self.bn2 = nn.BatchNorm1d(64)
        self.fc3 = nn.Linear(64, 32)
        self.bn3 = nn.BatchNorm1d(32)
        self.fc4 = nn.Linear(32, 8)
        self.bn4 = nn.BatchNorm1d(8)
        self.fc5 = nn.Linear(8, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.bn1(self.fc1(x)))
        x = self.relu(self.bn2(self.fc2(x)))
        x = self.relu(self.bn3(self.fc3(x)))
        x = self.relu(self.bn4(self.fc4(x)))
        x = self.fc5(x) 
        return x
    
model = RegressionModel(X_train.shape[1])
loss = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.005 )
epoch = 50
batch = 16
best_val_loss = float('inf')
patience = 5
counter = 0

print(X_train.shape, y_train.shape)
loss_list = []
for epopch in range(epoch):
    for i in range(0, len(X_train), batch):
        x_batch = X_train[i:i+batch]
        y_batch = y_train[i:i+batch]
        optimizer.zero_grad()
        y_pred = model(x_batch)
        loss_value = loss(y_pred, y_batch)
        loss_value.backward()
        optimizer.step()
        loss_list.append(loss_value.item())

    model.eval()
    with torch.no_grad():
        val_pred = model(X_test)
        val_loss = loss(val_pred, y_test)

    print(f'Epoch {epopch+1}/{epopch}, Loss:{loss_value.item()}, Val_loss:{val_loss}')

    if best_val_loss > val_loss:
        best_val_loss = val_loss
        counter = 0
    else:
        counter += 1
        if counter >= patience:
            print(f'Early stopping triggered at {epopch}')
            break

model_path = os.path.join(model_dir, 'park_slots_pred_model.pth')
torch.save(model.state_dict(), model_path)

true_values = y_test.numpy()
true_values = y_scaler.inverse_transform(true_values)
predicted_values = val_pred.numpy()
predicted_values = y_scaler.inverse_transform(predicted_values)


true_values = y_scaler.inverse_transform(true_values)
predicted_values = y_scaler.inverse_transform(predicted_values)

plt.figure(figsize=(10, 5))
plt.plot(true_values, label='Prawdziwe wartości', linewidth=2)
plt.plot(predicted_values, label='Przewidywane wartości', linestyle='--')
plt.xlabel('Próbka')
plt.ylabel('Liczba miejsc')
plt.title('Porównanie: Rzeczywiste vs Przewidywane')
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(loss_list, label='Strata', linewidth=2)
plt.xlabel('Iteracja')
plt.ylabel('Strata')
plt.title('Wykres Straty')
plt.legend()
plt.show()

for _ in range(5):
    random_index = random.randint(0, len(X_test) - 1)
    random_input = X_test[random_index].unsqueeze(0)
    predicted_value = model(random_input)
    predicted_value = y_scaler.inverse_transform(predicted_value.detach().numpy())
    print(f"Przewidywana liczba miejsc dla losowego wejścia: {predicted_value[0][0]}")
    print(f"Rzeczywista liczba miejsc: {true_values[random_index][0]}")

