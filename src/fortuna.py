import json
import random


class FortunaModel:
    def __init__(self, params_file="assets/best_params.json"):

        self.best_params = None
        self.best_mse = float('inf')
        self.params_file = params_file

        # Load existing parameters if they exist
        self.load_params()

    def fit(self, X, y, params):
        """IT is a simple linear model 
        e.g 
            y = a * X1 + b * X2 + c

        It then calculates the mean squared error.

        Args:
            X (Array(tuples)): A list of tuples where each tuple contains the independent parameters from our dataset
                e.g [(d['Total Time (ms)'], d['Interval Time (ms)'])] = [(140, 140), (710, 570),..]
            y (Array[int]): a list of target/result values for each of the tuples. its the heights in cm
            params (_type_): The params that the fortuna model created, The best model/best params for now

        Returns:
            tuple: it return the predictions and the mean squared error. (mse, predictions)
        """
        a, b, c = params
        predictions = [(a * x1 + b * x2 + c) for x1, x2 in X]
        mse = self.mean_squared_error(predictions, y)
        return mse, predictions

    def mean_squared_error(self, predictions, y):
        """calculate the mean squared err

        Args:
            predictions (Array[float]): array of the predictions. simply the results of the linear functions
            y (Array[int]): a list of target/result values for each of the tuples. its the heights in cm

        Returns:
            mse: float representing the mean squared error
                more info from: https://deepchecks.com/glossary/mean-square-error-mse/#:~:text=The%20MSE%20is%20the%20average,squaring%20the%20discrepancies%20is%20multifaceted.
                MSE is measured in square units. Using squared units instead of natural data units makes the interpretation less obvious.

                The objective of squaring the discrepancies is multifaceted.
                Squaring the differences removes negative mean squared error differences and guarantees that the squared mean error is always larger than or equal to zero. The value is usually always positive. Only a model without any errors will have an MSE of zero. This does not occur in actuality.
        """
        errors = [(pred - actual) ** 2 for pred, actual in zip(predictions, y)]
        mse = sum(errors) / len(errors)
        return mse

    def calibrate(self, data):
        """Calibrates the model. and tries to create better parameter every time its called. if it finds the better model it saves the parameters.

        Args:
            data (List[dicts{}]): a List of Dicts containing containing all the collected data.
                THe data is a List of this pydantic model:
                '''python
                    from pydantic import BaseModel, Field
                    from typing import List

                    class BounceData(BaseModel):
                        Height: int = Field(..., description="The height of the bounce in centimeters")
                        Bounce_Number: int = Field(..., alias="Bounce Number", description="The sequential number of the bounce")
                        Total_Time: str = Field(..., alias="Total Time", description="The total time taken in 'HH:MM.SS' format")
                        Interval_Time: str = Field(..., alias="Interval Time", description="The time interval between bounces in 'HH:MM.SS' format")
                        Total_Time_ms: int = Field(..., alias="Total Time (ms)", description="The total time in milliseconds")
                        Interval_Time_ms: int = Field(..., alias="Interval Time (ms)", description="The interval time in milliseconds")
                '''
        """
     
        X = [(d['Total Time (ms)'], d['Interval Time (ms)']) for d in data]
        y = [d['Height'] for d in data]

        for _ in range(1000):
            params = [random.uniform(-1, 1) for _ in range(3)]
            mse, _ = self.fit(X, y, params)

            if mse < self.best_mse:
                self.best_mse = mse
                self.best_params = params
                self.save_params()

    def predict(self, X):
        """Predicts the height for the given indipendent parameters(time in ms) 

        Args:
            X (Array(tuples)): A list of tuples where each tuple contains the indipendent parameters(time in ms) from our dataset
                e.g [(d['Total Time (ms)'], d['Interval Time (ms)'])] = [(140, 140), (710, 570),..]

        Raises:
            Exception: if the best params are not saved. just means you have to run self.calibrate(data) first

        Returns:
            Array[float]: array of the predictions
        """
        if self.best_params is None:
            raise Exception("Model is not calibrated yet.")
        a, b, c = self.best_params
        print("a, b, c:", a, b, c)
        print("Predictions:", [(a * x1 + b * x2 + c) for x1, x2 in X])
        # Calculate The predictions
        return [(a * x1 + b * x2 + c) for x1, x2 in X]

    def save_params(self):
        """save the best parameters and the best mean squared error as a json file
        """
        with open(self.params_file, 'w') as f:
            json.dump({'best_params': self.best_params,
                      'best_mse': self.best_mse}, f)

    def load_params(self):
        """Reads the the json file that containe the best parameters and the best mean squared error
        """
        try:
            with open(self.params_file, 'r') as f:
                params = json.load(f)
                self.best_params = params['best_params']
                self.best_mse = params['best_mse']
        except FileNotFoundError:
            pass
