from typing import Union
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import json

    
app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Load existing bounce data from CSV file
bounce_data_file = "src/tennis_ball_bounce_data.csv"
bounce_data_df = pd.read_csv(bounce_data_file)

# Convert CSV data to dictionary list format for model usage
bounce_data = bounce_data_df.to_dict(orient='records')

class FortunaModel:
    def __init__(self):
        self.coefficients = None

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        self.coefficients = np.linalg.lstsq(X, y, rcond=None)[0]

    def predict(self, X):
        X = np.array(X)
        return X @ self.coefficients

    def calibrate(self, data):
        X = [[d['Total Time (ms)'], d['Interval Time (ms)']] for d in data]
        y = [d['Height'] for d in data]
        self.fit(X, y)

model = FortunaModel()
model.calibrate(bounce_data)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TenniScale</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <script src="/assets/timer.js" defer></script>
        </head>
        <body class="bg-blue-100 font-sans leading-normal tracking-normal">
            <div class="container mx-auto p-4">
                <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                    <h1 class="text-2xl font-bold mb-4 text-center text-blue-600">Welcome to TenniScale!</h1>
                    <div class="text-center mb-6">
                        <button id="startButton" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">Start Timer</button>
                        <button id="stopButton" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" disabled>Stop Timer</button>
                        <button id="recordBounceButton" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" disabled>Record Bounce</button>
                    </div>
                    <div class="text-center mb-6">
                        <p>Elapsed Time: <span id="elapsedTime">0.00</span> seconds</p>
                    </div>
                    <form action="/api/measure" method="post" class="text-center">
                        <input type="hidden" id="total_time_ms" name="total_time_ms">
                        <input type="hidden" id="interval_time_ms" name="interval_time_ms">
                        <div class="mb-4">
                            <label for="height" class="block text-gray-700 text-sm font-bold mb-2">Height (cm):</label>
                            <input type="number" id="height" name="height" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required>
                        </div>
                        <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Submit Measurement</button>
                    </form>
                    <div class="text-center mt-6">
                        <a href="/api/results" class="text-blue-500 hover:text-blue-800">View Results</a>
                    </div>
                </div>
            </div>
        </body>
        </html>

    """

@app.post("/api/measure")
async def submit_data(height: float = Form(...), total_time_ms: float = Form(...), interval_time_ms: float = Form(...)):
    bounce_data.append({
        'Height': height,
        'Total Time (ms)': total_time_ms,
        'Interval Time (ms)': interval_time_ms
    })
    model.calibrate(bounce_data)
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/calibrate")
async def calibrate_model():
    model.calibrate(bounce_data)
    return {"message": "Model calibrated successfully!"}

@app.get("/api/results", response_class=HTMLResponse)
async def get_results():
    df = pd.DataFrame(bounce_data)

    fig, ax = plt.subplots()
    for height in df['Height'].unique():
        subset = df[df['Height'] == height]
        ax.plot(subset['Total Time (ms)'], subset['Interval Time (ms)'], marker='o', label=f'Height {height} cm')

    ax.set_xlabel('Total Time (ms)')
    ax.set_ylabel('Interval Time (ms)')
    ax.set_title('Interval Time (ms) vs Total Time (ms) for Different Heights')
    ax.legend()
    ax.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')

    return f"""
    <html>
    <head>
        <title>Measurement Results</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-blue-100 font-sans leading-normal tracking-normal">
        <div class="container mx-auto p-4">
            <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <h1 class="text-2xl font-bold mb-4 text-center text-blue-600">Measurement Results</h1>
                <img src="data:image/png;base64,{img_str}" class="mx-auto">
                <br>
                <div class="text-center">
                    <a href="/" class="text-blue-500 hover:text-blue-800">Back</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/predict")
async def predict_height(total_time_ms: float, interval_time_ms: float):
    features = [total_time_ms, interval_time_ms]
    predicted_height = model.predict([features])[0]
    return {"predicted_height": predicted_height}

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
