document.addEventListener('DOMContentLoaded', function() {
    loadConfig();
});

function loadConfig() {
    fetch('/config/data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('REGRESSION_SHEET_KEY').value = data.REGRESSION_SHEET_KEY;
            document.getElementById('MANTIS_TICKETS_NEXUS_E6').value = data.MANTIS_TICKETS_NEXUS_E6;
            document.getElementById('REGRESSION_FILTER_ID').value = data.REGRESSION_FILTER_ID;
            document.getElementById('JOB_INTERVAL_MINUTES').value = data.JOB_INTERVAL_MINUTES;
        })
        .catch(err => console.error(err));
}

function saveConfig() {
    const data = {
        REGRESSION_SHEET_KEY: document.getElementById('REGRESSION_SHEET_KEY').value,
        MANTIS_TICKETS_NEXUS_E6: document.getElementById('MANTIS_TICKETS_NEXUS_E6').value,
        REGRESSION_FILTER_ID: document.getElementById('REGRESSION_FILTER_ID').value,
        JOB_INTERVAL_MINUTES: parseInt(document.getElementById('JOB_INTERVAL_MINUTES').value)
    };

    fetch('/config/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        alert(result.message);
        
        // Update scheduler separately if interval was changed
        updateJobInterval(data.JOB_INTERVAL_MINUTES);
    })
    .catch(err => console.error(err));
}

function updateJobInterval(interval) {
    fetch('/config/update_interval', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({interval: interval})
    })
    .then(response => response.json())
    .then(result => {
        console.log(result.message);
    })
    .catch(err => console.error(err));
}

function goBack() {
    window.location.href = '/';
}
