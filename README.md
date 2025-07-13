# WeatherFlow4Py

A Python library for interacting with the WeatherFlow REST API and WebSocket services. This library provides both synchronous and asynchronous interfaces to access weather data from WeatherFlow weather stations.

[![PyPI](https://img.shields.io/pypi/v/weatherflow4py.svg)](https://pypi.org/project/weatherflow4py/)
[![Test PyPI](https://img.shields.io/badge/Test%20PyPI-available-blue)](https://test.pypi.org/project/weatherflow4py/)

## Features

- **REST API Client**: Access station data, forecasts, and observations
- **WebSocket Client**: Real-time weather data updates
- **Type Annotations**: Full type support for better development experience
- **Asynchronous Support**: Built with `asyncio` for efficient I/O operations
- **Pydantic Models**: Strongly-typed data models for all API responses

## Installation

```bash
pip install weatherflow4py
```

## Prerequisites

- Python 3.12 or higher
- WeatherFlow API token (available from [WeatherFlow's website](https://tempestwx.com))

## Quick Start

### REST API Example

```python
import asyncio
from weatherflow4py.api import WeatherFlowRestAPI

async def main():
    # Initialize the API with your token
    async with WeatherFlowRestAPI("YOUR_API_TOKEN") as api:
        # Get all available stations
        stations = await api.async_get_stations()
        
        for station in stations.stations:
            print(f"Station: {station.name}")
            print(f"Location: {station.latitude}, {station.longitude}")
            
            # Get current observations
            obs = await api.async_get_observation(station.station_id)
            print(f"Current temperature: {obs.obs[0].air_temperature}°C")
            
            # Get forecast
            forecast = await api.async_get_forecast(station.station_id)
            print(f"Forecast high: {forecast.forecast.daily[0].air_temp_high}°C")

if __name__ == "__main__":
    asyncio.run(main())
```

### WebSocket Example

```python
import asyncio
import logging
from weatherflow4py.ws import WeatherFlowWebsocketAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Initialize the WebSocket client
    ws = WeatherFlowWebsocketAPI("YOUR_API_TOKEN")
    
    # Define callback functions for different message types
    def handle_observation(data):
        print(f"Observation received - Temp: {data.air_temperature}°C")
    
    def handle_rapid_wind(data):
        print(f"Wind speed: {data.wind_speed} m/s at {data.wind_direction}°")
    
    # Register callbacks
    ws.register_callback("obs_st", handle_observation)
    ws.register_callback("rapid_wind", handle_rapid_wind)
    
    try:
        # Start listening for messages
        await ws.connect()
        
        # Start listening to all available devices
        await ws.start_listening()
        
        # Keep the connection alive
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("Disconnecting...")
    finally:
        await ws.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Documentation

### REST API

The `WeatherFlowRestAPI` class provides the following methods:

- `async_get_stations()`: Get all stations associated with the account
- `async_get_observation(station_id)`: Get current observations for a station
- `async_get_forecast(station_id)`: Get forecast data for a station
- `async_get_device_observations(device_id)`: Get observations from a specific device
- `get_all_data()`: Get all available data for all stations

### WebSocket API

The `WeatherFlowWebsocketAPI` class provides real-time updates:

- `connect()`: Establish WebSocket connection
- `disconnect()`: Close the connection
- `start_listening(device_ids=None)`: Start listening for updates
- `stop_listening(device_ids=None)`: Stop listening for updates
- `register_callback(message_type, callback)`: Register a callback for specific message types

## Error Handling

The library raises specific exceptions for different error conditions:

- `TokenError`: When no API token is provided
- `APIError`: For general API errors
- `WebSocketError`: For WebSocket connection issues

## Rate Limiting

- **REST API**: Limited to 100 requests per minute
- **WebSocket**: Follows WeatherFlow's rate limiting policies

## Resources

- [WeatherFlow API Documentation](https://apidocs.tempestwx.com/reference/quick-start)
- [WeatherFlow REST API Swagger](https://weatherflow.github.io/Tempest/api/swagger/)
- [WeatherFlow WebSocket Documentation](https://weatherflow.github.io/Tempest/api/ws.html)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- WeatherFlow for their excellent weather station hardware and API
- All contributors who have helped improve this library

## Support

For support, please open an issue on the [GitHub repository](https://github.com/jeeftor/weatherflow4py).
