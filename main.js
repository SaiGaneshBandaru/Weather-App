document.addEventListener('DOMContentLoaded', () => {
  const cityInput = document.getElementById('cityInput');
  const searchBtn = document.getElementById('searchBtn');
  const message = document.getElementById('message');
  const result = document.getElementById('result');
  const forecastSection = document.getElementById('forecast');
  const forecastContainer = document.getElementById('forecastContainer');

  function showMessage(text, isError = false) {
    message.textContent = text;
    message.style.color = isError ? '#b00020' : '#475569';
  }

  function setResultHidden(hidden) {
    if (hidden) {
      result.classList.add('hidden');
      result.classList.remove('show'); // hide fade-in animation
      forecastSection.classList.add('hidden');
    } else {
      result.classList.remove('hidden');
    }
  }

  async function fetchWeather(city) {
    setResultHidden(true);
    showMessage('Loading...');
    try {
      // Current weather
      const res = await fetch(`/weather?city=${encodeURIComponent(city)}`);
      const data = await res.json();
      if (!res.ok) {
        showMessage(data.error || 'Could not fetch weather', true);
        return;
      }

      // Update current weather
      document.getElementById('cityName').textContent = data.city || city;
      document.getElementById('country').textContent = data.country || '';
      document.getElementById('temp').textContent = `${Math.round(data.temp)}°C`;
      document.getElementById('desc').textContent = data.description || '';
      document.getElementById('humidity').textContent = data.humidity ?? '-';
      document.getElementById('wind').textContent = data.wind_speed ?? '-';
      document.getElementById('pressure').textContent = data.pressure ?? '-';
      document.getElementById('sunrise').textContent = data.sunrise ?? '-';
      document.getElementById('sunset').textContent = data.sunset ?? '-';

      const iconEl = document.getElementById('weatherIcon');
      if (data.icon) {
        iconEl.src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
        iconEl.style.display = '';
      } else {
        iconEl.style.display = 'none';
      }

      setResultHidden(false);
      result.classList.add('show'); // fade-in animation
      showMessage('');

      // Fetch 3-day forecast
      const forecastRes = await fetch(`/forecast?city=${encodeURIComponent(city)}`);
      const forecastData = await forecastRes.json();

      if (!forecastRes.ok) {
        showMessage(forecastData.error || 'Could not fetch forecast', true);
        return;
      }

      // Render forecast cards
      forecastContainer.innerHTML = ''; // clear previous
      forecastData.forEach(day => {
        const card = document.createElement('div');
        card.className = 'forecast-card';
        card.innerHTML = `
          <div>${day.date}</div>
          <img src="https://openweathermap.org/img/wn/${day.icon}@2x.png" alt="icon" width="50">
          <div>Min: ${Math.round(day.min)}°C</div>
          <div>Max: ${Math.round(day.max)}°C</div>
        `;
        forecastContainer.appendChild(card);
      });
      forecastSection.classList.remove('hidden');
    } catch (err) {
      showMessage('Network error — please try again', true);
    }
  }

  searchBtn.addEventListener('click', () => {
    const city = cityInput.value.trim();
    if (!city) {
      showMessage('Please enter a city name', true);
      return;
    }
    fetchWeather(city);
  });

  cityInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchBtn.click();
  });
});
