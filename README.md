# TenniScale

Welcome to **TenniScale**! A fun and innovative way to measure height using a tennis ball. This project uses various techniques to measure height and applies the Fortuna model to ensure accuracy.

![TenniScale Logo](./assets/logo.png) <!-- Replace with the actual link to your logo once created -->

## Project Overview

The idea for TenniScale came from a group of Swedes who wanted to measure their height in a more entertaining and engaging way. The concept revolves around using a tennis ball and developing a novel approach to accurately measure height. By leveraging the Fortuna model, we aim to refine and enhance the measurement accuracy despite the inherent challenges.

## Materials

To get started with TenniScale, you'll need the following materials:
- A tennis ball
- A ruler

## Measuring Techniques

We explored several techniques to measure height using a tennis ball:

1. **Measuring from when it leaves the ball:**
   - This method involves starting the measurement as soon as the ball is released. However, it includes a lot of human error.

2. **Measuring from when acceleration is 0:**
   - In this approach, the ball is not thrown but released gently. A more accurate method would be to throw the ball into the air and measure from the point where acceleration is zero. The challenge here is determining the exact height at that point.

3. **Time till the ball stops bouncing:**
   - By timing the duration until the ball stops bouncing, we can get multiple data points. This method is somewhat unclean but provides at least four points for analysis.

4. **Time between every bounce:**
   - This technique involves measuring the time taken between each bounce as laps, providing additional data for refining the height measurement.

## Measure Points

For calibration and testing, the following height points are used:
- 200 cm
- 180 cm
- 160 cm
- 140 cm
- 120 cm
- 100 cm
- 80 cm
- 60 cm
- 40 cm
- 20 cm

## Getting Started

To get started with TenniScale, you can use Python. Here's the boilerplate code to set up your environment:

```python
from typing import Union
from fastapi import FastAPI

app = FastAPI()

import debugpy
debugpy.listen(("0.0.0.0", 5678))

@app.get("/")
def read_root():
    return {"Hello": "World ass wiper"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

This code is set up in a devcontainer, but you can also run it in a virtual environment or directly on your host system.

## Repository

Check out the TenniScale project on GitHub: [TenniScale](https://github.com/valiantlynx/TenniScale.git)

---

Feel free to contribute to the project, report issues, or suggest new features!

---

Happy measuring with TenniScale!

### Next Steps

- **Create the Logo:** Use the concept provided to design a logo or hire a designer to create it for you.
- **Host the Logo Image:** Once you have the logo, host it on a platform like GitHub, Imgur, or your project repository and replace the placeholder link in the README.
- **Finalize and Push the README:** Save the README file as `README.md` in your project root directory and push it to your GitHub repository.
