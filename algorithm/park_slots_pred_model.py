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

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32)

class RegressionModel(nn.Module):
    def __init__(self, input_size):
        super(RegressionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 32)
        self.fc2 = nn.Linear(32, 8)
        self.fc3 = nn.Linear(8, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x) 
        return x
model = RegressionModel(X_train.shape[1])
loss = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001 )
epoch = 100
batch = 16
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
    print(f'Epoch {epopch+1}/{epoch}, Loss: {loss_value.item()}')
torch.save(model.state_dict(), 'park_slots_pred_model.pth')


model.eval()
with torch.no_grad():
    y_pred_test = model(X_test)
    test_loss = loss(y_pred_test, y_test)
    print(f"Test MSE: {test_loss.item()}")

true_values = y_test.numpy()
predicted_values = y_pred_test.numpy()

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

random_index = random.randint(0, len(X_test) - 1)
random_input = X_test[random_index].unsqueeze(0)
predicted_value = model(random_input)
predicted_value = y_scaler.inverse_transform(predicted_value.detach().numpy())
print(f"Przewidywana liczba miejsc dla losowego wejścia: {predicted_value[0][0]}")
print(f"Rzeczywista liczba miejsc: {true_values[random_index][0]}")

