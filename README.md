# Crypto Trading Data Processor

A Flask web application for processing cryptocurrency trading data and generating detailed reports using FIFO (First In, First Out) methodology.

## 🚀 Features

### 1. No Limit Output
- Complete transaction history for all coins
- No time restrictions
- Maintains running balance
- FIFO method for buy/sell matching
- Handles unclosed positions

### 2. Days Limit Output
- Recent transactions within specified days
- Focuses on settled transactions only
- Customizable days limit (10, 15, etc.)
- Filters sell transactions by date while keeping all buy records

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd AccountWebDev
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

4. **Access the application:**
```
http://localhost:3000
```

## 📖 How to Use

### Step 1: Upload File
- Upload your Excel file (.xlsx, .xls) or CSV file
- The application will automatically validate the file format and required columns

### Step 2: Choose Processing Type
- **No Limit Output**: For complete transaction history
- **Days Limit Output**: For recent transactions (specify number of days)

### Step 3: Generate Report
- Click the process button
- View results in the preview table
- Download the generated CSV file

## 📊 Output Format

The generated CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| **ASSET** | Coin name (TRX, BNB, ETH, etc.) |
| **Sell Date** | Date of sell transaction |
| **Sell Amount** | Quantity sold |
| **Buy Date** | Date of corresponding buy transaction |
| **Buy Amount Used** | Quantity from buy transaction used |
| **Buy Price** | Price per unit at buy |
| **Sell Price** | Price per unit at sell |
| **Cost Basis** | Total cost of buy transaction |
| **Proceeds** | Total proceeds from sell transaction |
| **P/L** | Profit/Loss calculation |
| **TDS** | Tax Deducted at Source |
| **REMARK** | Status (DONE, ERROR, or BALANCE CARRIED FORWARD) |

## 🔧 Technical Details

### Backend
- **Framework**: Flask (Python)
- **Data Processing**: Pandas
- **File Handling**: Excel/CSV processing with openpyxl and xlrd

### Frontend
- **UI**: HTML, CSS, JavaScript
- **Styling**: Bootstrap for responsive design
- **Interactivity**: AJAX for seamless file processing

### Algorithm
- **Method**: FIFO (First In, First Out)
- **Matching**: Buy records matched with sell transactions
- **Balance Tracking**: In-memory balance maintenance
- **Error Handling**: Graceful handling of insufficient buy records

## 📁 Project Structure

```
AccountWebDev/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Generated output files (auto-created)
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
└── .gitignore           # Git ignore rules
```

## 🔍 Error Handling

The application handles various scenarios:

- **Missing buy data**: When sell transactions don't have corresponding buy records
- **Unclosed positions**: Buy records that haven't been sold yet
- **Invalid file format**: Non-Excel/CSV files
- **Missing columns**: Files without required data columns
- **Network issues**: Graceful error handling with user-friendly messages

## 📝 Required File Format

Your input file should contain these columns:
- `Date`: Transaction date
- `Action`: Buy or Sell
- `Coin`: Cryptocurrency name
- `Quantity`: Transaction amount
- `Price in Base currency`: Price per unit
- `Total Price in Base currency`: Total transaction value
- `Tds`: Tax Deducted at Source (optional)

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
For production deployment, consider using:
- Gunicorn or uWSGI as WSGI server
- Nginx as reverse proxy
- Environment variables for configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For any issues or questions, please:
1. Check the existing issues
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🔄 Version History

- **v1.0.0**: Initial release with FIFO logic and web interface
- **v1.1.0**: Added days limit functionality
- **v1.2.0**: Improved error handling and UI enhancements 