from typing import Union
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from src.fortuna import FortunaModel
import matplotlib.pyplot as plt
import io
import base64


app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Load existing bounce data from CSV file
bounce_data_file = "src/tennis_ball_bounce_data.csv"
bounce_data_df = pd.read_csv(bounce_data_file)
full_bounce_data_df = pd.read_csv(bounce_data_file)

# Consider only the first four bounces ? or three ?
bounce_data_df = bounce_data_df[bounce_data_df['Bounce Number'] <= 4]

# Convert CSV data to dictionary list format for model
bounce_data = bounce_data_df.to_dict(orient='records')
full_bounce_data = full_bounce_data_df.to_dict(orient='records')

model = FortunaModel()
model.calibrate(bounce_data)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serves back html to the client side. the html is connected with a styles.css and a timer.js.
    styles.css is for extra styling on top of the tailwind classes
    timer.js is for the timer functionality in the client side.

    Returns:
        str: HTML to be rendred by the browser
    """    
    await calibrate_model() # might be a better way that doing it on start up. The best params are saved so no worries anyway
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TenniScale</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/assets/styles.css">
            <script src="/assets/timer.js" defer></script>
            <link rel="icon" type="image/x-icon" href="/assets/logo.jpg">
        </head>
        <body class="bg-custom-olive font-sans leading-normal tracking-normal">
            <div class="container mx-auto p-4">
                <div class="bg-custom-dark shadow-md rounded px-8 pt-6 pb-8 mb-4">
                    <h1 class="text-2xl font-bold mb-4 text-center text-custom-black">Welcome to TenniScale!</h1>
                    <div class="text-center mb-6">
                        <button id="startButton" class="bg-custom-lime hover-bg-custom-dark text-custom-gray font-bold py-2 px-4 rounded">Start Timer</button>
                        <button id="stopButton" class="bg-custom-olive hover-bg-custom-dark text-custom-gray font-bold py-2 px-4 rounded" disabled>Stop Timer</button>
                        <button id="recordBounceButton" class="bg-custom-pale-olive hover-bg-custom-dark text-custom-gray font-bold py-2 px-4 rounded" disabled>Record Bounce</button>
                    </div>
                    <div class="text-center mb-6">
                        <p class="text-custom-black">Elapsed Time: <span id="elapsedTime">0.00</span> seconds</p>
                    </div>
                    <!-- Form to submit data for calibration -->
                    <form action="/api/measure" method="post" class="text-center mb-6">
                        <input type="hidden" id="total_time_ms" name="total_time_ms">
                        <input type="hidden" id="interval_time_ms" name="interval_time_ms">
                        <div class="mb-4">
                            <label for="height" class="block text-custom-black text-sm font-bold mb-2">Height (cm):</label>
                            <input type="number" id="height" name="height" class="shadow appearance-none border rounded w-full py-2 px-3 text-custom-black leading-tight focus:outline-none focus:shadow-outline" required>
                        </div>
                        <button type="submit" class="bg-custom-pale-olive hover-bg-custom-dark text-custom-gray font-bold py-2 px-4 rounded">Submit Measurement for Calibration</button>
                    </form>
                    <!-- Form to trigger prediction -->
                    <form action="/api/predict" method="post" class="text-center">
                        <input type="hidden" id="total_time_ms_predict" name="total_time_ms">
                        <input type="hidden" id="interval_time_ms_predict" name="interval_time_ms">
                        <button type="submit" class="bg-custom-lime hover-bg-custom-dark text-custom-gray font-bold py-2 px-4 rounded">Predict Height</button>
                    </form>
                    <div class="text-center mt-6">
                        <a href="/api/results" class="text-custom-black hover:text-custom-gray">View Results</a>
                    </div>
                </div>
            </div>
        </body>
        </html>

    """


@app.post("/api/measure")
async def submit_data(height: float = Form(...), total_time_ms: float = Form(...), interval_time_ms: float = Form(...)):
    """handles the data that is submited from the clientside incase the user clicks submit data for calibration.

    Args:
        height (float, optional): The height of the user in centimeters. Defaults to Form(...).
        total_time_ms (float, optional): The total time recorded. it not important from the fourth bouce and on. Defaults to Form(...).
        interval_time_ms (float, optional): the time between the bounces. Defaults to Form(...).

    Returns:
        RedirectResponse: redirects you back to the root of the site
    """
    bounce_data.append({
        'Height': height,
        'Total Time (ms)': total_time_ms,
        'Interval Time (ms)': interval_time_ms
    })
    model.calibrate(bounce_data)
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/calibrate")
async def calibrate_model():
    """calls the calibrate model function with the our dataset. maybe ill call it on startup or something

    Returns:
        dict: message of success
    """
    model.calibrate(bounce_data)
    return {"message": "Model calibrated successfully!"}


@app.get("/api/results", response_class=HTMLResponse)
async def get_results():
    """Generates and returns an HTML page displaying various visualizations and model metrics 
    based on bounce data.

    The function performs the following steps:
    1. Loads bounce data into pandas DataFrames for analysis.
    2. Creates several plots:
        - Scatter Plot: Shows the relationship between "Interval Time" and "Total Time" 
          across different bounce heights.
        - Line Plots: Illustrates "Total Time" and "Interval Time" over the bounce number 
          for different heights.
        - Histogram: Displays the distribution of bounce numbers. not really important but what the hell
        - Box Plot: Summarizes the distribution of "Total Time" and "Interval Time". i dont know
    3. Retrieves and displays the best parameters and Mean Squared Error (MSE) 
       from a machine learning model.
    4. Embeds the plots and metrics into an HTML page using Tailwind CSS and some custom css for styling.

    Returns:
        HTMLResponse: An HTML page containing the visualizations and model metrics.
    """  
    df = pd.DataFrame(bounce_data)
    full_df = pd.DataFrame(full_bounce_data)

    # Scatter Plot: Interval Time vs Total Time for Different Heights
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
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    img_str1 = base64.b64encode(buf1.read()).decode('utf-8')
    plt.close(fig1)

    # Line Plots: Total Time and Interval Time Over Bounce Number for All Bounces
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
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    img_str2 = base64.b64encode(buf2.read()).decode('utf-8')
    plt.close(fig2)

    # Histogram of Bounce Numbers
    fig3, ax4 = plt.subplots(figsize=(12, 6))
    max_bounce = int(full_df['Bounce Number'].max())
    ax4.hist(full_df['Bounce Number'], bins=range(
        1, max_bounce + 2), edgecolor='black')
    ax4.set_xlabel('Bounce Number')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Histogram of Bounce Numbers')
    ax4.grid(True)
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png')
    buf3.seek(0)
    img_str3 = base64.b64encode(buf3.read()).decode('utf-8')
    plt.close(fig3)

    # Box Plot of Total Time and Interval Time
    fig4, ax5 = plt.subplots(figsize=(12, 6))
    df[['Total Time (ms)', 'Interval Time (ms)']].plot.box(ax=ax5)
    ax5.set_title('Box Plot of Total Time and Interval Time')
    ax5.grid(True)
    buf4 = io.BytesIO()
    plt.savefig(buf4, format='png')
    buf4.seek(0)
    img_str4 = base64.b64encode(buf4.read()).decode('utf-8')
    plt.close(fig4)

    # Retrieve best params and MSE from the model
    best_params = model.best_params
    best_mse = model.best_mse

    # Display the results including the best parameters and MSE
    return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Measurement Results</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/assets/styles.css">
            <link rel="icon" type="image/x-icon" href="/assets/logo.jpg">
        </head>
        <body class="bg-custom-olive font-sans leading-normal tracking-normal">
            <div class="container mx-auto p-4">
                <div class="bg-custom-dark shadow-md rounded px-8 pt-6 pb-8 mb-4">
                    <h1 class="text-2xl font-bold mb-4 text-center text-custom-black">Measurement Results</h1>
                    <div class="mb-4">
                        <h2 class="text-xl font-semibold text-center text-custom-black">Best Parameters and MSE</h2>
                        <p class="text-center text-lg text-custom-black">Best Parameters: {best_params}</p>
                        <p class="text-center text-lg text-custom-black">Best MSE: {best_mse:.4f}</p>
                    </div>

                    <div class="mb-4">
                        <h2 class="text-xl font-semibold text-center text-custom-black">Interval Time vs Total Time for Different Heights</h2>
                        <img src="data:image/png;base64,{img_str1}" class="mx-auto">
                    </div>

                    <div class="mb-4">
                        <h2 class="text-xl font-semibold text-center text-custom-black">Total Time and Interval Time Over Bounce Number</h2>
                        <img src="data:image/png;base64,{img_str2}" class="mx-auto">
                    </div>

                    <div class="mb-4">
                        <h2 class="text-xl font-semibold text-center text-custom-black">Histogram of Bounce Numbers</h2>
                        <img src="data:image/png;base64,{img_str3}" class="mx-auto">
                    </div>

                    <div class="mb-4">
                        <h2 class="text-xl font-semibold text-center text-custom-black">Box Plot of Total Time and Interval Time</h2>
                        <img src="data:image/png;base64,{img_str4}" class="mx-auto">
                    </div>

                    <div class="text-center">
                        <a href="/" class="text-custom-black hover-text-custom-dark">Back</a>
                    </div>
                </div>
            </div>
        </body>
        </html>

    """


@app.post("/api/predict")
async def predict_height(total_time_ms: float = Form(...), interval_time_ms: float = Form(...)):
    """use the model to predict the height

    Args:
        total_time_ms (float, optional): The total time recorded. it not important from the fourth bouce and on. Defaults to Form(...).
        interval_time_ms (float, optional): the time between the bounces. Defaults to Form(...).

    Returns:
        HTMLResponse: the html including the prediction
    """    
    features = [total_time_ms, interval_time_ms]
    predicted_height = model.predict([(features)])[0] # the predict function can handle multiple predicts at the same time. and i gave it only a list of 1 tuple the prediction on index 1 is the correct prediction 

    return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prediction Result</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/assets/styles.css">
            <link rel="icon" type="image/x-icon" href="/assets/logo.jpg">
        </head>
        <body class="bg-custom-olive font-sans leading-normal tracking-normal">
            <div class="container mx-auto p-4">
                <div class="bg-custom-dark shadow-md rounded px-8 pt-6 pb-8 mb-4">
                    <h1 class="text-2xl font-bold mb-4 text-center text-custom-black">Prediction Result</h1>
                    <div class="text-center">
                        <p class="text-lg font-semibold text-custom-black">Predicted Height: {predicted_height:.2f} cm</p>
                    </div>
                    <div class="text-center mt-6">
                        <a href="/" class="text-custom-black hover-text-custom-dark">Back</a>
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
