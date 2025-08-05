from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_action(action):
    """Normalize action to handle case variations"""
    if pd.isna(action):
        return None
    action_str = str(action).strip().lower()
    if action_str in ['buy', 'b']:
        return 'Buy'
    elif action_str in ['sell', 's']:
        return 'Sell'
    else:
        return None

def process_trading_data(df, days_limit=None):
    """
    Process trading data with improved FIFO logic and in-memory balance tracking
    """
    try:
        # Convert date column to datetime - handle both string and datetime formats
        if df['Date'].dtype == 'object':
            # If dates are strings, try to parse them
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # If already datetime, no conversion needed
        
        # Normalize Action column to handle case variations
        df['Action'] = df['Action'].apply(normalize_action)
        
        # Check for invalid actions
        invalid_actions = df[df['Action'].isna()]
        if len(invalid_actions) > 0:
            invalid_values = invalid_actions['Action'].unique()
            raise ValueError(f"Invalid Action values found: {invalid_values}. Only 'Buy'/'Sell' (case insensitive) are allowed.")
        
        # Filter by days limit if specified
        if days_limit:
            # Get the latest date in the data
            latest_date = df['Date'].max()
            # Calculate cutoff date as N days before the latest date
            cutoff_date = latest_date - timedelta(days=days_limit)
            
            # IMPORTANT: Only filter Sell records by date, keep ALL Buy records
            # This ensures we have enough Buy records to match with recent Sells
            sell_mask = (df['Action'] == 'Sell') & (df['Date'] >= cutoff_date)
            buy_mask = df['Action'] == 'Buy'
            df = df[sell_mask | buy_mask]
        
        # Sort by date
        df = df.sort_values(['Coin', 'Date'])
        
        # Initialize output data
        output_data = []
        processing_errors = []
        
        # Process each coin separately
        for coin in df['Coin'].unique():
            coin_data = df[df['Coin'] == coin].copy()
            coin_data = coin_data.sort_values('Date')
            
            # Initialize buy records queue (FIFO) - in memory only
            buy_records = []
            
            for idx, row in coin_data.iterrows():
                if row['Action'] == 'Buy':
                    # Add to buy records queue (FIFO)
                    buy_records.append({
                        'date': row['Date'],
                        'amount': row['Quantity'],
                        'price': row['Price in  Base currency'],
                        'total_cost': row['Total Price in Base currency']
                    })
                    
                elif row['Action'] == 'Sell':
                    sell_amount = row['Quantity']
                    sell_price = row['Price in  Base currency']
                    sell_date = row['Date']
                    sell_total = row['Total Price in Base currency']
                    tds = row['Tds'] if pd.notna(row['Tds']) else 0
                    
                    # Calculate total available buy amount
                    total_available_buy = sum(record['amount'] for record in buy_records)
                    
                    if total_available_buy < sell_amount:
                        # Not enough buy records - settle available amount and show error for remaining
                        # No warning needed as this is normal processing behavior
                        
                        # First, settle the available buy records (if any)
                        if total_available_buy > 0:
                            remaining_sell = total_available_buy  # Only sell what's available
                            buy_details = []
                            
                            while remaining_sell > 0 and buy_records:
                                buy_record = buy_records[0]  # FIFO - take first buy record
                                available_buy = buy_record['amount']
                                
                                if available_buy <= remaining_sell:
                                    # Use entire buy record
                                    used_amount = available_buy
                                    buy_records.pop(0)  # Remove from queue
                                else:
                                    # Use partial buy record
                                    used_amount = remaining_sell
                                    buy_records[0]['amount'] -= remaining_sell
                                    # Recalculate total_cost for remaining amount
                                    remaining_ratio = buy_records[0]['amount'] / available_buy
                                    buy_records[0]['total_cost'] = buy_record['total_cost'] * remaining_ratio
                                
                                # Calculate cost basis for this portion
                                cost_basis = used_amount * buy_record['price']
                                proceeds = used_amount * sell_price
                                
                                # Store buy details for display
                                buy_details.append({
                                    'date': buy_record['date'],
                                    'price': buy_record['price'],
                                    'amount': used_amount,
                                    'cost_basis': cost_basis,
                                    'proceeds': proceeds
                                })
                                
                                remaining_sell -= used_amount
                            
                            # Generate output rows for settled portion
                            for i, buy_detail in enumerate(buy_details):
                                sell_amount_display = buy_detail['amount']
                                sell_date_display = sell_date.strftime('%d/%m/%Y %H:%M:%S')
                                
                                # TDS proportional to settled amount
                                settled_ratio = buy_detail['amount'] / sell_amount
                                tds_display = round(tds * settled_ratio, 2)
                                    
                                # Calculate P/L for this portion
                                pl = buy_detail['proceeds'] - buy_detail['cost_basis']
                                pl_display = round(pl, 2) if pl != 0 else 'NIL'
                                
                                # Add to output for settled portion
                                output_data.append({
                                    'ASSET': coin,
                                    'Sell Date': sell_date_display,
                                    'Sell Amount': sell_amount_display,
                                    'Buy Date': buy_detail['date'].strftime('%d/%m/%Y %H:%M:%S'),
                                    'Buy Amount Used': buy_detail['amount'],
                                    'Buy Price': buy_detail['price'],
                                    'Sell Price': sell_price,
                                    'Cost Basis': round(buy_detail['cost_basis'], 2),
                                    'Proceds USDT': 'NIL',
                                    'Proceeds': round(buy_detail['proceeds'], 2),
                                    'P/L': pl_display,
                                    'TDS': tds_display,
                                    'REMARK': 'DONE'
                                })
                        
                        # Now add error row for the remaining unsold amount
                        remaining_unsold = sell_amount - total_available_buy
                        if remaining_unsold > 0:
                            # TDS proportional to error amount
                            error_ratio = remaining_unsold / sell_amount
                            error_tds = round(tds * error_ratio, 2)
                            
                            output_data.append({
                                'ASSET': coin,
                                'Sell Date': sell_date.strftime('%d/%m/%Y %H:%M:%S'),
                                'Sell Amount': remaining_unsold,
                                'Buy Date': 'NIL',
                                'Buy Amount Used': 'NIL',
                                'Buy Price': 'NIL',
                                'Sell Price': sell_price,
                                'Cost Basis': 'NIL',
                                'Proceds USDT': 'NIL',
                                'Proceeds': round(remaining_unsold * sell_price, 2),
                                'P/L': 'NIL',
                                'TDS': error_tds,  # Proportional TDS on error portion
                                'REMARK': f'ERROR - INSUFFICIENT BUY RECORDS (Available: {total_available_buy})'
                            })
                        continue
                    
                    # Match sell with buy records (FIFO method)
                    remaining_sell = sell_amount
                    buy_details = []
                    
                    while remaining_sell > 0 and buy_records:
                        buy_record = buy_records[0]  # FIFO - take first buy record
                        available_buy = buy_record['amount']
                        
                        if available_buy <= remaining_sell:
                            # Use entire buy record
                            used_amount = available_buy
                            buy_records.pop(0)  # Remove from queue
                        else:
                            # Use partial buy record
                            used_amount = remaining_sell
                            buy_records[0]['amount'] -= remaining_sell
                            # Recalculate total_cost for remaining amount
                            remaining_ratio = buy_records[0]['amount'] / available_buy
                            buy_records[0]['total_cost'] = buy_record['total_cost'] * remaining_ratio
                        
                        # Calculate cost basis for this portion
                        cost_basis = used_amount * buy_record['price']
                        proceeds = used_amount * sell_price
                        
                        # Store buy details for display
                        buy_details.append({
                            'date': buy_record['date'],
                            'price': buy_record['price'],
                            'amount': used_amount,
                            'cost_basis': cost_basis,
                            'proceeds': proceeds
                        })
                        
                        remaining_sell -= used_amount
                    
                    # Generate output rows for each buy record used
                    for i, buy_detail in enumerate(buy_details):
                        # Each row should show the actual amount used from this buy record
                        sell_amount_display = buy_detail['amount']  # Always use the actual amount used
                        sell_date_display = sell_date.strftime('%d/%m/%Y %H:%M:%S')
                        
                        # TDS only on first row of a sell transaction
                        if i == 0:
                            tds_display = tds
                        else:
                            tds_display = 0
                            
                        # Calculate P/L for this portion
                        pl = buy_detail['proceeds'] - buy_detail['cost_basis']
                        pl_display = round(pl, 2) if pl != 0 else 'NIL'
                        
                        # Add to output with exact NOLIMIT OUTPUT format
                        output_data.append({
                            'ASSET': coin,
                            'Sell Date': sell_date_display,
                            'Sell Amount': sell_amount_display,
                            'Buy Date': buy_detail['date'].strftime('%d/%m/%Y %H:%M:%S'),
                            'Buy Amount Used': buy_detail['amount'],
                            'Buy Price': buy_detail['price'],
                            'Sell Price': sell_price,
                            'Cost Basis': round(buy_detail['cost_basis'], 2),
                            'Proceds USDT': 'NIL',
                            'Proceeds': round(buy_detail['proceeds'], 2),
                            'P/L': pl_display,
                            'TDS': tds_display,
                            'REMARK': 'DONE'
                        })
            
            # Add remaining buy records (unclosed positions) to output
            for buy_record in buy_records:
                output_data.append({
                    'ASSET': coin,
                    'Sell Date': 'NIL',
                    'Sell Amount': 'NIL',
                    'Buy Date': buy_record['date'].strftime('%d/%m/%Y %H:%M:%S'),
                    'Buy Amount Used': buy_record['amount'],
                    'Buy Price': buy_record['price'],
                    'Sell Price': 'NIL',
                    'Cost Basis': round(buy_record['total_cost'], 2),
                    'Proceds USDT': 'NIL',
                    'Proceeds': 'NIL',
                    'P/L': 'NIL',
                    'TDS': 0,
                    'REMARK': 'BALANCE CARRIED FORWARD'
                })
        
        # Sort output data to match NOLIMIT OUTPUT order exactly
        output_df = pd.DataFrame(output_data)
        if len(output_df) > 0:
            # Sort by ASSET in specific order, then by Sell Date
            asset_order = ['TRX', 'BNB', 'ETH', 'XRP', 'USDT']
            output_df['Asset_Order'] = output_df['ASSET'].map({asset: i for i, asset in enumerate(asset_order)})
            output_df['Sort_Date'] = pd.to_datetime(output_df['Sell Date'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            output_df = output_df.sort_values(['Asset_Order', 'Sort_Date'], na_position='last')
            output_df = output_df.drop(['Asset_Order', 'Sort_Date'], axis=1)
        
        return output_df, processing_errors
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return None, [{'message': f'Data processing error: {str(e)}'}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Please upload Excel (.xlsx, .xls) or CSV file'})
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        # Read file based on extension
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Validate required columns
        required_columns = ['Date', 'Action', 'Coin', 'Quantity', 'Price in  Base currency', 'Total Price in Base currency']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({'success': False, 'error': f'Missing required columns: {", ".join(missing_columns)}'})
        
        # Process data for both outputs
        output_df_nolimit, errors_nolimit = process_trading_data(df, days_limit=None)
        
        # Get days limit from form
        days_limit = request.form.get('days_limit', '10')
        try:
            days_limit = int(days_limit)
        except ValueError:
            days_limit = 10
        
        output_df_dayslimit, errors_dayslimit = process_trading_data(df, days_limit=days_limit)
        
        if output_df_nolimit is None or output_df_dayslimit is None:
            return jsonify({'success': False, 'error': 'Failed to process data'})
        
        # Generate output files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_nolimit = f'output_nolimit_{timestamp}.csv'
        out_dayslimit = f'output_{days_limit}days_{timestamp}.csv'
        
        path_nolimit = os.path.join(app.config['UPLOAD_FOLDER'], out_nolimit)
        path_dayslimit = os.path.join(app.config['UPLOAD_FOLDER'], out_dayslimit)
        
        output_df_nolimit.to_csv(path_nolimit, index=False)
        output_df_dayslimit.to_csv(path_dayslimit, index=False)
        
        # Prepare error messages for frontend
        all_errors = errors_nolimit + errors_dayslimit
        error_messages = []
        for error in all_errors:
            if 'message' in error:
                error_messages.append(error['message'])
        
        return jsonify({
            'success': True,
            'nolimit_preview': output_df_nolimit.to_dict('records'),
            'dayslimit_preview': output_df_dayslimit.to_dict('records'),
            'nolimit_file': out_nolimit,
            'dayslimit_file': out_dayslimit,
            'days_limit': days_limit,
            'errors': error_messages,
            'has_errors': len(error_messages) > 0})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing file: {str(e)}'})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000) 