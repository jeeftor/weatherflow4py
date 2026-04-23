# Changelog

All notable changes to this project will be documented in this file.
## [1.5.3] - 2026-04-23

### Bug Fixes

- Make air temperature optional and fix all ty type errors

### CI/CD

- Add git-cliff changelog generation and improve release-drafter config

### Testing

- Add comprehensive tests boosting coverage from 73% to 95%

## [1.5.1] - 2026-03-29

### CI/CD

- Fix uv pip install missing --system flag in release workflow

### Features

- Make wind observations and related fields optional (v1.5.1)

## [1.5.0] - 2026-03-29

### Bug Fixes

- Resolve ty errors, add pip-audit hook, and upgrade vulnerable deps

### CI/CD

- Version bump
- Fix release workflow by replacing tomli with stdlib tomllib

### Features

- Initial test of uv migration push to github
- Make ForecastHourly.sea_level_pressure and precip_probability optional

## [1.3.2] - 2025-06-18

### Features

- Updated optionality and test for precip which appears to be optional

## [0.2.22] - 2024-07-03

### Ha

- Add pressure and precipititation probability to hourly forecast

## [0.1.9] - 2023-12-28


