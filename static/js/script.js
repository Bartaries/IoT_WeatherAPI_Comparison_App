document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const cityInput = document.getElementById('city-input');
    const temperatureValue = document.getElementById('temperature-value');
    const humidityValue = document.getElementById('humidity-value');
    const lastSyncTime = document.getElementById('last-sync-time');
    const soilIndicator = document.getElementById('soil-indicator');
    const soilIndicatorIcon = document.getElementById('soil-indicator-icon');
    const eventLog = document.getElementById('event-log');
    const chartCanvas = document.getElementById('sensor-chart');
    const deviceStatusText = document.getElementById('device-status-text');
    const deviceStatusIcon = document.getElementById('device-status-icon');
    const weatherDisplayCard = document.getElementById('weather-display-card');
    const state = {
        apiTime: null,
        iotTime: null
    };

    let chart;
    const chartLabels = Array.from({ length: 12 }, (_, i) => `${(i * 2)}h ago`);
    const initialTempData = Array.from({ length: 12 }, () => Math.random() * 5 + 20);
    const initialHumidData = Array.from({ length: 12 }, () => Math.random() * 10 + 60);

   
    const fetchWeather = async (query) => {
        const cleanQuery = query.trim();
        
        if (cleanQuery == '') {
            addLog("Easter Egg activated: Space Weather.");
            return handleSpaceWeather();
        }

        try {
            const response = await fetch(`/api/weather?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.details?.error?.message || 'Nie znaleziono lokalizacji.');
            }
            const data = await response.json();
            addLog("API data received successfuly.");
            updateWeatherUI(data);
            return true;
        } catch (error) {
            console.error(error);
            addLog(`Błąd: ${error.message}`);
            return false;
        }
    };

    let fetchWeatherIot = (async query => {
        try {
            const response = await fetch('/iot/weather');
            if (!response.ok) {
                throw new Error(`Error HTTP! Status: ${response.status}`);
            }

            const iotData = await response.json();

            if (!Array.isArray(iotData.allReceived) || iotData.allReceived === 0) {
            console.error("Is not an array or is empty.");
            return null;
            }

            let timestamp = iotData.lastTimestamp;
            let temperature = iotData.lastTemperature;
            let humidity = iotData.lastHumidity;
            let soil = iotData.lastSoilIndicator;
         
            return {
                timestamp,
                temperature,
                humidity,
                soil,
                iotData
                };

        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    });

    const updateWeatherUI = (data, isSpaceWeather = false) => {
        if (!data || !data.forecast || !data.forecast.forecastday || data.forecast.forecastday.length === 0) {
            console.error('Received wrong API:', data);
            addLog("Incomplete server answer.");
            return;
        }

        if (isSpaceWeather) {
        weatherDisplayCard.classList.add('bg-dark', 'text-white');
        weatherDisplayCard.classList.remove('bg-white', 'current-weather-card');
        document.getElementById('rain-chance-container').innerHTML = `<i class="fas fa-satellite"></i> Cosmic Dust: 0%`;
        document.getElementById('dew-point').textContent = `Dew point N/A`;
        document.getElementById('sunrise-time').textContent = 'N/A';
        document.getElementById('sunset-time').textContent = 'N/A';
        document.getElementById('hourly-forecast-container').innerHTML = '<p class="text-white-50">No hourly forecast in Deep Space.</p>';

    } else {
        weatherDisplayCard.classList.remove('bg-dark', 'text-white');
        weatherDisplayCard.classList.add('bg-white', 'current-weather-card');
    }

        const { location, current, forecast } = data;
        const todayForecast = forecast.forecastday[0];

        document.getElementById('location-name').textContent = `${location.name}, ${location.country}`;
        state.apiTime = current.last_updated;
        document.getElementById('current-timestamp').textContent = `Ostatnia aktualizacja: ${new Date(state.apiTime).toLocaleString('pl-PL')}`;
        document.getElementById('main-temp').textContent = `${Math.round(current.temp_c)}°C`;
        document.getElementById('weather-description').textContent = current.condition.text;
        document.getElementById('weather-icon-container').innerHTML = `<img src="https:${current.condition.icon}" alt="${current.condition.text}" style="width: 64px; height: 64px;">`;
        document.getElementById('high-low-temp').textContent = `Max: ${Math.round(todayForecast.day.maxtemp_c)}°C / Min: ${Math.round(todayForecast.day.mintemp_c)}°C`;
        document.getElementById('feels-like').textContent = `Odczuwalna: ${Math.round(current.feelslike_c)}°C`;
        document.getElementById('rain-chance-container').innerHTML = `<i class="fas fa-umbrella"></i> Szansa opadów: ${todayForecast.day.daily_chance_of_rain}%`;
        document.getElementById('dew-point').textContent = `Dew point ${current.dewpoint_c}°C`;
        document.getElementById('sunrise-time').textContent = todayForecast.astro.sunrise;
        document.getElementById('sunset-time').textContent = todayForecast.astro.sunset;

        const hourlyContainer = document.getElementById('hourly-forecast-container');
        hourlyContainer.innerHTML = '';
        const currentHour = new Date().getHours();
        todayForecast.hour.filter(h => new Date(h.time).getHours() >= currentHour).forEach(hour => {
            const hourElement = document.createElement('div');
            hourElement.className = 'hourly-item';
            hourElement.innerHTML = `
                <p class="fw-bold mb-1">${new Date(hour.time).getHours()}:00</p>
                <img src="https:${hour.condition.icon}" alt="${hour.condition.text}" width="40" height="40">
                <p class="fw-bold mt-1 mb-0">${Math.round(hour.temp_c)}°C</p>
                <small class="text-muted"><i class="fas fa-umbrella"></i> ${hour.chance_of_rain}%</small>
            `;
            hourlyContainer.appendChild(hourElement);

        });
    };


    const initWeather = async () => {
        let success = false;
        if (navigator.geolocation) {
            success = await new Promise(resolve => {
                navigator.geolocation.getCurrentPosition(
                    (position) => resolve(fetchWeather(`${position.coords.latitude},${position.coords.longitude}`)),
                    () => resolve(fetchWeather('Wroclaw'))
                );
            });
        } else {
            success = await fetchWeather('Wroclaw');
        }
        return success;
    };

    function addLog(message) {
        const alertsContainer = document.getElementById('alerts-container');
        const newLogDiv = document.createElement('div');
 
        newLogDiv.className = 'log-item alert alert-info py-2 mb-2 flex items-center space-x-2'; 
        newLogDiv.setAttribute('role', 'alert');

        const time = new Date().toLocaleTimeString();
        const contentHTML = `
            <i class="fas fa-info-circle"></i>
            <span class="text-gray-400">${time}</span>
            <span class="text-gray-700">${message}</span>
        `;
        newLogDiv.innerHTML = contentHTML;

        alertsContainer.prepend(newLogDiv);
        
        const allLogs = alertsContainer.querySelectorAll('.log-item');
        const maxLogs = 10; 

        if (allLogs.length > maxLogs) {
            const oldestLog = allLogs[allLogs.length - 1];
            alertsContainer.removeChild(oldestLog);
        }
}

    async function updateReadings() {
        try {
            let result = await fetchWeatherIot();

            if (!result || !result.temperature || !result.humidity || !result.timestamp) {
                addLog('No necessary values from IoT device.');
                return false;
            }

            let { timestamp, temperature, humidity, soil } = result

            if(soil){soil >= 1; soilIndicatorIcon.classList.remove('text-warning'); soilIndicatorIcon.classList.add('text-success');}
            else{soil == 0 ; soilIndicatorIcon.classList.remove('text-success'); soilIndicatorIcon.classList.add('text-warning');};
            
            state.iotTime = timestamp;
            temperatureValue.textContent = `${temperature}°C`;
            humidityValue.textContent = `${humidity}%`;
            lastSyncTime.textContent = state.iotTime;
            soilIndicator.innerHTML = `${soil}%`;

            if (chart) {
                chart.data.datasets[0].data.shift();
                chart.data.datasets[0].data.push(parseFloat(temperature));
                chart.data.datasets[1].data.shift();
                chart.data.datasets[1].data.push(parseFloat(humidity));
                chart.data.labels.shift();
                chart.data.labels.push('Now');
                chart.update('none');
            }
            addLog("IoT data received successfuly.");
            return true;

        } catch (error) {
            console.error(error);
            addLog('IoT sync problem.');
            return false;
        }
    }

    function checkDeviceSyncStatus(minutesLimit = 15) {
            addLog("Multisource time sync status.");
            const parseIotDate = (iotString) => {
                const [datePart, timePart] = iotString.split(' ');
                const [day, month, year] = datePart.split('-');
                const [hours, minutes, seconds] = timePart.split(':');
                return new Date(`20${year}`, month - 1, day, hours, minutes, seconds);
            };

            const parseApiDate = (apiString) => {
                return new Date(apiString);
            };

            function checkDeviceSyncStatus(minutesLimit = 15) {
                if (!state.apiTime || !state.iotTime) {
                    addLog("No timestamp data.");
                    return false; 
                }
            }

            const apiDate = parseApiDate(state.apiTime);
            const iotDate = parseIotDate(state.iotTime);
            const apiTimeMs = apiDate.getTime();
            const iotTimeMs = iotDate.getTime();
            const timeDifferenceMs = Math.abs(apiTimeMs - iotTimeMs);
            const limitMs = minutesLimit * 60 * 1000;
            addLog(`Min time difference between devices is ${minutesLimit} min for Online status.`);
            const isOffline = timeDifferenceMs > limitMs;
            const timeDifferenceMinutes = Math.round(timeDifferenceMs / 60000);
            addLog(`Delay between API and IoT: ${timeDifferenceMinutes} min.`);

            return isOffline;
        }

    function toggleDeviceStatus(isOffline) {
        if(!isOffline) {
                deviceStatusText.textContent = 'Online';
                deviceStatusText.classList.remove('text-red-600');
                deviceStatusText.classList.add('text-green-600');
                deviceStatusIcon.className = 'fas fa-2x fa-link fa-fade text-lg text-success mb-2';
                addLog('Device reconnected.');
        } else {
            deviceStatusText.textContent = 'Offline';
            deviceStatusText.classList.remove('text-green-600');
            deviceStatusText.classList.add('text-red-600');
            deviceStatusIcon.className = 'fas fa-2x fa-link fa-fade text-lg text-error mb-2';
            addLog('Device connection lost.');
        }
    }

    function createChart() {
        const ctx = chartCanvas.getContext('2d');
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: initialTempData,
                    borderColor: 'rgba(239, 68, 68, 0.8)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Humidity (%)',
                    data: initialHumidData,
                    borderColor: 'rgba(59, 130, 246, 0.8)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y1',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Temperature (°C)',
                            color: 'rgba(239, 68, 68, 1)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Humidity (%)',
                            color: 'rgba(59, 130, 246, 1)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'top',
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index',
                },
            }
        });
    }

    const handleSpaceWeather = () => {
        const spaceData = {
            location: {
                name: "Deep Space",
                country: "The Universe"
            },
            current: {
                last_updated: new Date().toISOString().replace('T', ' ').substring(0, 19),
                temp_c: -270,
                condition: {
                    text: "Cosmic Microwave Background",
                    icon: "//cdn.weatherapi.com/weather/64x64/night/113.png"
                },
                feelslike_c: -270,
                dewpoint_c: 'N/A'
            },
            forecast: {
                forecastday: [{
                    day: {
                        maxtemp_c: -270,
                        mintemp_c: -272.15,
                        daily_chance_of_rain: 0 
                    },
                    astro: {
                        sunrise: 'N/A',
                        sunset: 'N/A'
                    },
                    hour: []
                }]
            }
        };

        updateWeatherUI(spaceData, true);
        return true;
    };

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const cityCleaned = cityInput.value.trim();
        const cityRaw = cityInput.value; 
        if (cityRaw.length > 0) { 
            
            const apiSuccess = await fetchWeather(cityCleaned); 
            const iotSuccess = await updateReadings();
            
            if (apiSuccess && iotSuccess) {
                checkDeviceSyncStatus();
            }
            
            addLog(`New city: ${cityCleaned}`);
            cityInput.value = '';
        }
    });

    createChart();
    async function mainOrchestrator() {
        addLog('Chart initialized.');
        const apiSuccess = await initWeather();
        addLog(`Loading weather from API: ${apiSuccess}`);
        const iotSuccess = await updateReadings();
        addLog(`Loading weather from IoT: ${iotSuccess}`);
        
        if (apiSuccess && iotSuccess) {
            toggleDeviceStatus(checkDeviceSyncStatus());
        } else {
             toggleDeviceStatus(true); 
        }
    }
    addLog('Dashboard initialized successfully.');

    setInterval(async () => {
            await fetchWeather(cityInput.value.trim());
            const iotSuccess = await updateReadings();
            
            if (state.apiTime && iotSuccess) {
                checkDeviceSyncStatus();
            }
        }, 30000);

    setInterval(createChart, 1*60*60*1000)

    mainOrchestrator();
});