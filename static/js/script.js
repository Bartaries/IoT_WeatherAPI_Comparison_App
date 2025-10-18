document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const cityInput = document.getElementById('city-input');

    const fetchWeather = async (query) => {
        try {
            const response = await fetch(`/api/weather?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.details?.error?.message || 'Nie znaleziono lokalizacji.');
            }
            const data = await response.json();
            updateWeatherUI(data);
        } catch (error) {
            console.error('Błąd pobierania danych pogodowych:', error);
            alert(`Błąd: ${error.message}`);
        }
    };

    const updateWeatherUI = (data) => {
        if (!data || !data.forecast || !data.forecast.forecastday || data.forecast.forecastday.length === 0) {
            console.error('Otrzymano nieprawidłowe dane z API:', data);
            alert('Wystąpił błąd podczas przetwarzania danych pogodowych. Odpowiedź serwera jest niekompletna.');
            return;
        }

        const { location, current, forecast } = data;
        const todayForecast = forecast.forecastday[0];

        document.getElementById('location-name').textContent = `${location.name}, ${location.country}`;
        document.getElementById('current-timestamp').textContent = `Ostatnia aktualizacja: ${new Date(current.last_updated).toLocaleString('pl-PL')}`;
        document.getElementById('main-temp').textContent = `${Math.round(current.temp_c)}°C`;
        document.getElementById('weather-description').textContent = current.condition.text;
        document.getElementById('weather-icon-container').innerHTML = `<img src="https:${current.condition.icon}" alt="${current.condition.text}" style="width: 64px; height: 64px;">`;
        document.getElementById('high-low-temp').textContent = `Max: ${Math.round(todayForecast.day.maxtemp_c)}°C / Min: ${Math.round(todayForecast.day.mintemp_c)}°C`;
        document.getElementById('feels-like').textContent = `Odczuwalna: ${Math.round(current.feelslike_c)}°C`;
        document.getElementById('rain-chance-container').innerHTML = `<i class="fas fa-umbrella"></i> Szansa opadów: ${todayForecast.day.daily_chance_of_rain}%`;

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

        const alertsContainer = document.getElementById('alerts-container');
        alertsContainer.innerHTML = `<div class="alert alert-info py-2" role="alert"><i class="fas fa-info-circle"></i> Brak aktywnych alertów dla tego regionu.</div>`;

    };

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = cityInput.value.trim();
        if (city) {
            fetchWeather(city);
            cityInput.value = '';
        }
    });

    const initWeather = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => fetchWeather(`${position.coords.latitude},${position.coords.longitude}`),
                () => fetchWeather('Wroclaw')
            );
        } else {
            fetchWeather('Wroclaw');
        }
    };
            const temperatureValue = document.getElementById('temperature-value');
            const humidityValue = document.getElementById('humidity-value');
            const lastSyncTime = document.getElementById('last-sync-time');
            const eventLog = document.getElementById('event-log');
            const chartCanvas = document.getElementById('sensor-chart');

            let chart;
            const chartLabels = Array.from({ length: 12 }, (_, i) => `${(i * 2)}h ago`);
            const initialTempData = Array.from({ length: 12 }, () => Math.random() * 5 + 20);
            const initialHumidData = Array.from({ length: 12 }, () => Math.random() * 10 + 60);

            function addLog(message) {
                const li = document.createElement('li');
                li.className = 'flex items-center space-x-2';
                const time = new Date().toLocaleTimeString();
                li.innerHTML = `<span class="text-gray-400">${time}</span><span class="text-gray-700">${message}</span>`;
                eventLog.prepend(li);
                if (eventLog.children.length > 5) {
                    eventLog.removeChild(eventLog.lastChild);
                }
            }

            function updateReadings() {
                const newTemp = (Math.random() * 2 - 1 + parseFloat(temperatureValue.textContent)).toFixed(1);
                const newHumidity = Math.round(Math.random() * 4 - 2 + parseInt(humidityValue.textContent));

                temperatureValue.textContent = `${newTemp}°C`;
                humidityValue.textContent = `${newHumidity}%`;

                lastSyncTime.textContent = new Date().toLocaleString();
                
                addLog('New sensor data received.');
                if (chart) {
                    chart.data.datasets[0].data.shift();
                    chart.data.datasets[0].data.push(newTemp);
                    chart.data.datasets[1].data.shift();
                    chart.data.datasets[1].data.push(newHumidity);
                    chart.data.labels.shift();
                    chart.data.labels.push('Now');
                    chart.update('none');
                }
            }

            function toggleDeviceStatus() {
                isOnline = !isOnline;
                if(isOnline) {
                    deviceStatusText.textContent = 'Online';
                    deviceStatusText.classList.remove('text-red-600');
                    deviceStatusText.classList.add('text-green-600');
                    deviceStatusIcon.className = 'fas fa-signal text-lg text-green-600';
                    addLog('Device reconnected.');
                } else {
                    deviceStatusText.textContent = 'Offline';
                    deviceStatusText.classList.remove('text-green-600');
                    deviceStatusText.classList.add('text-red-600');
                    deviceStatusIcon.className = 'fas fa-exclamation-triangle text-lg text-red-600';
                    addLog('Device connection lost.', true);
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

            initWeather();
            createChart();
            updateReadings();
            addLog('Dashboard initialized successfully.');


            setInterval(updateReadings, 5000);
        });