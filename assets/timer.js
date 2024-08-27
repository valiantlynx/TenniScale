let startTime, interval, bounces = [];
const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const recordBounceButton = document.getElementById('recordBounceButton');
const elapsedTimeSpan = document.getElementById('elapsedTime');
const totalTimeInput = document.getElementById('total_time_ms');
const intervalTimeInput = document.getElementById('interval_time_ms');

// Start Timer
function startTimer() {
    startTime = new Date();
    interval = setInterval(updateTime, 100);
    startButton.disabled = true;
    stopButton.disabled = false;
    recordBounceButton.disabled = false;
}

// Stop Timer
function stopTimer() {
    clearInterval(interval);
    startButton.disabled = false;
    stopButton.disabled = true;
    recordBounceButton.disabled = true;
    totalTimeInput.value = (new Date() - startTime) / 1000; // in seconds
    calculateInterval();
}

// Record Bounce
function recordBounce() {
    let now = new Date();
    let bounceTime = (now - startTime) / 1000; // in seconds
    bounces.push(bounceTime);
    calculateInterval();
}

function updateTime() {
    let now = new Date();
    let elapsed = (now - startTime) / 1000; // in seconds
    elapsedTimeSpan.textContent = elapsed.toFixed(2);
}

function calculateInterval() {
    if (bounces.length > 1) {
        const lastBounce = bounces[bounces.length - 1];
        const previousBounce = bounces[bounces.length - 2];
        const interval = (lastBounce - previousBounce) * 1000; // in milliseconds
        intervalTimeInput.value = interval.toFixed(0);
    } else {
        intervalTimeInput.value = 0;
    }
}

// Event Listeners
document.addEventListener('keydown', (event) => {
    if (event.code === 'Enter') {
        startTimer();
    } else if (event.code === 'Space') {
        recordBounce();
        event.preventDefault(); // Prevent default spacebar scrolling behavior
    } else if (event.code === 'Escape') {
        stopTimer();
        event.preventDefault();
    }
});
recordBounceButton.addEventListener('click', recordBounce);
startButton.addEventListener('click', startTimer);
stopButton.addEventListener('click', stopTimer);
