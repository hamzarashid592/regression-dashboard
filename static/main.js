function triggerJob() {
    fetch('/trigger', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(err => console.error(err));
}

function checkStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('job-status').innerText = data.last_status;
            document.getElementById('progress-bar').value = data.progress;
        })
        .catch(err => console.error(err));
}

function goToConfig() {
    window.location.href = '/config';
}

function downloadLog() {
    const date = document.getElementById('log-date').value;
    if (!date) {
        alert('Please select a date!');
        return;
    }

    window.location.href = `/logs?date=${date}`;
}


let nextRunTime = null;
let countdownInterval = null;

function fetchScheduleStatus() {
    fetch('/schedule/status')
        .then(response => response.json())
        .then(data => {
            if (data.next_run) {
                document.getElementById('next-run-time').innerText = data.next_run;
                nextRunTime = new Date(data.next_run.replace(' UTC', 'Z'));  // ISO date
                startCountdown();
            } else {
                document.getElementById('next-run-time').innerText = 'Not scheduled';
                clearInterval(countdownInterval);
            }
        })
        .catch(err => console.error(err));
}

function startCountdown() {
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }

    countdownInterval = setInterval(() => {
        if (!nextRunTime) return;

        const now = new Date();
        let diff = Math.floor((nextRunTime - now) / 1000); // seconds

        if (diff <= 0) {
            document.getElementById('countdown-timer').innerText = 'Running soon...';
            clearInterval(countdownInterval);
            return;
        }

        const hours = Math.floor(diff / 3600).toString().padStart(2, '0');
        const minutes = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
        const seconds = Math.floor(diff % 60).toString().padStart(2, '0');

        document.getElementById('countdown-timer').innerText = `${hours}:${minutes}:${seconds}`;
    }, 1000);
}

// Poll every 10 seconds for next run info
setInterval(fetchScheduleStatus, 10000);
fetchScheduleStatus();  // Run immediately on load
