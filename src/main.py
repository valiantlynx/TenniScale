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
import random

app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Load existing bounce data from CSV file
bounce_data_file = "src/tennis_ball_bounce_data.csv"
bounce_data_df = pd.read_csv(bounce_data_file)

# Consider only the first four bounces
bounce_data_df = bounce_data_df[bounce_data_df['Bounce Number'] <= 4]

# Convert CSV data to dictionary list format for model usage
bounce_data = bounce_data_df.to_dict(orient='records')

class FortunaModel:
    def __init__(self):
        self.best_params = None
        self.best_mse = float('inf')

    def fit(self, X, y, params):
        # Simple linear model y = a * X1 + b * X2 + c
        a, b, c = params
        predictions = a * X[:, 0] + b * X[:, 1] + c
        mse = np.mean((predictions - y) ** 2)
        return mse, predictions

    def calibrate(self, data):
        X = np.array([[d['Total Time (ms)'], d['Interval Time (ms)']] for d in data])
        y = np.array([d['Height'] for d in data])

        for _ in range(1000):  # Try 1000 random parameter sets
            params = [random.uniform(-1, 1) for _ in range(3)]  # Random coefficients a, b, c
            mse, _ = self.fit(X, y, params)

            if mse < self.best_mse:
                self.best_mse = mse
                self.best_params = params

    def predict(self, X):
        X = np.array(X)
        if self.best_params is None:
            raise Exception("Model is not calibrated yet.")
        a, b, c = self.best_params
        return a * X[:, 0] + b * X[:, 1] + c

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
                    <!-- Form to submit data for calibration -->
                    <form action="/api/measure" method="post" class="text-center mb-6">
                        <input type="hidden" id="total_time_ms" name="total_time_ms">
                        <input type="hidden" id="interval_time_ms" name="interval_time_ms">
                        <div class="mb-4">
                            <label for="height" class="block text-gray-700 text-sm font-bold mb-2">Height (cm):</label>
                            <input type="number" id="height" name="height" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required>
                        </div>
                        <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Submit Measurement for Calibration</button>
                    </form>
                    <!-- Form to trigger prediction -->
                    <form action="/api/predict" method="post" class="text-center">
                        <input type="hidden" id="total_time_ms_predict" name="total_time_ms">
                        <input type="hidden" id="interval_time_ms_predict" name="interval_time_ms">
                        <button type="submit" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">Predict Height</button>
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

    # 1. Scatter Plot: Interval Time vs Total Time for Different Heights
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    for height in df['Height'].unique():
        subset = df[df['Height'] == height]
        ax1.scatter(subset['Total Time (ms)'], subset['Interval Time (ms)'],
                    label=f'Height {height} cm', alpha=0.7)
    ax1.set_xlabel('Total Time (ms)')
    ax1.set_ylabel('Interval Time (ms)')
    ax1.set_title(
        'Interval Time (ms) vs Total Time (ms) for Different Heights')
    ax1.legend()
    ax1.grid(True)

    # Save first figure to buffer
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    img_str1 = base64.b64encode(buf1.read()).decode('utf-8')
    plt.close(fig1)  # Close the figure to free up memory

    # 2. Line Plots: Total Time and Interval Time Over Bounce Number for All Bounces
    fig2, (ax2, ax3) = plt.subplots(1, 2, figsize=(12, 6))

    for height in df['Height'].unique():
        height_data = df[df['Height'] == height]
        ax2.plot(height_data['Bounce Number'], height_data['Total Time (ms)'],
                 marker='o', label=f'Height {height} cm')
        ax3.plot(height_data['Bounce Number'], height_data['Interval Time (ms)'],
                 marker='o', label=f'Height {height} cm')

    ax2.set_xlabel('Bounce Number')
    ax2.set_ylabel('Total Time (ms)')
    ax2.set_title('Total Time vs Bounce Number')
    ax2.legend()
    ax2.grid(True)

    ax3.set_xlabel('Bounce Number')
    ax3.set_ylabel('Interval Time (ms)')
    ax3.set_title('Interval Time vs Bounce Number')
    ax3.legend()
    ax3.grid(True)

    plt.tight_layout()

    # Save second figure to buffer
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    img_str2 = base64.b64encode(buf2.read()).decode('utf-8')
    plt.close(fig2)  # Close the figure to free up memory
    
    # 3. Histogram of Bounce Numbers
    fig3, ax4 = plt.subplots(figsize=(12, 6))
    max_bounce = int(df['Bounce Number'].max())  # Convert to int
    ax4.hist(df['Bounce Number'], bins=range(
        1, max_bounce + 2), edgecolor='black')
    ax4.set_xlabel('Bounce Number')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Histogram of Bounce Numbers')
    ax4.grid(True)

    # Save third figure to buffer
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png')
    buf3.seek(0)
    img_str3 = base64.b64encode(buf3.read()).decode('utf-8')
    plt.close(fig3)  # Close the figure to free up memory

    # 4. Box Plot of Total Time and Interval Time
    fig4, ax5 = plt.subplots(figsize=(12, 6))
    df[['Total Time (ms)', 'Interval Time (ms)']].plot.box(ax=ax5)
    ax5.set_title('Box Plot of Total Time and Interval Time')
    ax5.grid(True)

    # Save fourth figure to buffer
    buf4 = io.BytesIO()
    plt.savefig(buf4, format='png')
    buf4.seek(0)
    img_str4 = base64.b64encode(buf4.read()).decode('utf-8')
    plt.close(fig4)  # Close the figure to free up memory

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
                <div class="mb-4">
                    <h2 class="text-xl font-semibold text-center text-blue-500">Interval Time vs Total Time for Different Heights</h2>
                    <img src="data:image/png;base64,{img_str1}" class="mx-auto">
                </div>
                <div class="mb-4">
                    <h2 class="text-xl font-semibold text-center text-blue-500">Total Time and Interval Time Over Bounce Number</h2>
                    <img src="data:image/png;base64,{img_str2}" class="mx-auto">
                </div>
                <div class="mb-4">
                    <h2 class="text-xl font-semibold text-center text-blue-500">Histogram of Bounce Numbers</h2>
                    <img src="data:image/png;base64,{img_str3}" class="mx-auto">
                </div>
                <div class="mb-4">
                    <h2 class="text-xl font-semibold text-center text-blue-500">Box Plot of Total Time and Interval Time</h2>
                    <img src="data:image/png;base64,{img_str4}" class="mx-auto">
                </div>
                <br>
                <div class="text-center">
                    <a href="/" class="text-blue-500 hover:text-blue-800">Back</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/api/predict")
async def predict_height(total_time_ms: float = Form(...), interval_time_ms: float = Form(...)):
    # Use the Fortuna model to predict height
    features = [total_time_ms, interval_time_ms]
    predicted_height = model.predict([features])[0]

    return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prediction Result</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body class="bg-blue-100 font-sans leading-normal tracking-normal">
            <div class="container mx-auto p-4">
                <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                    <h1 class="text-2xl font-bold mb-4 text-center text-blue-600">Prediction Result</h1>
                    <div class="text-center">
                        <p class="text-lg font-semibold">Predicted Height: {predicted_height:.2f} cm</p>
                    </div>
                    <div class="text-center mt-6">
                        <a href="/" class="text-blue-500 hover:text-blue-800">Back</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """)

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
