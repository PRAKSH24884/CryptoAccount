# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Docker support with Dockerfile and docker-compose.yml
- Comprehensive documentation (README.md, DEPLOYMENT.md, CONTRIBUTING.md)
- Sample data file for testing
- WSGI entry point for production deployment
- MIT License

### Changed
- Improved error handling with user-friendly messages
- Enhanced UI responsiveness
- Better file validation

### Fixed
- FIFO logic improvements for partial settlements
- TDS calculation accuracy
- Date filtering logic for days limit output

## [1.2.0] - 2024-01-15

### Added
- Days limit functionality for recent transaction processing
- Improved error handling and validation
- Enhanced UI with Bootstrap styling
- File upload validation
- Download functionality for generated reports

### Changed
- Updated FIFO algorithm for better accuracy
- Improved data processing performance
- Enhanced user interface design

### Fixed
- Fixed TDS calculation issues
- Resolved partial settlement logic
- Corrected date filtering for sell transactions

## [1.1.0] - 2024-01-10

### Added
- Web interface with file upload
- Real-time processing feedback
- CSV output generation
- Error handling for invalid data

### Changed
- Migrated from command-line to web application
- Improved data validation
- Enhanced user experience

## [1.0.0] - 2024-01-05

### Added
- Initial release with FIFO logic
- Basic data processing functionality
- Support for Excel and CSV files
- Core trading data analysis features

### Features
- Buy/sell transaction matching using FIFO method
- Running balance tracking
- Profit/Loss calculation
- TDS handling
- Multiple cryptocurrency support

---

## Version History

- **v1.0.0**: Initial release with core FIFO functionality
- **v1.1.0**: Added web interface and improved user experience
- **v1.2.0**: Enhanced with days limit feature and better error handling
- **Unreleased**: Docker support and comprehensive documentation

## Migration Guide

### From v1.1.0 to v1.2.0
- No breaking changes
- New days limit feature is optional
- All existing functionality remains the same

### From v1.0.0 to v1.1.0
- Application now runs as web service instead of command-line
- File upload through web interface required
- Output files are automatically generated and downloadable

## Known Issues

- Large files (>16MB) may cause memory issues
- Very old date formats might need manual conversion
- Some Excel files with complex formatting may not load correctly

## Upcoming Features

- API endpoints for programmatic access
- Additional export formats (PDF, JSON)
- Advanced filtering and sorting options
- Real-time data processing for large datasets
- Multi-language support 