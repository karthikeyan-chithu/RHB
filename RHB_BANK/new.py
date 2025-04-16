from flask import Flask, render_template, request, send_file, session
import pymysql
from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'rhb_statement_generator_secret_key'  # Required for sessions

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Write the index.html template with explicit UTF-8 encoding
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html>
  <head>
    <title>RHB Statement Generator</title>
    <meta charset="UTF-8">
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #eef3f7;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
      }

      .form-box {
        background-color: #fff;
        padding: 30px 40px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        width: 100%;
        max-width: 400px;
        text-align: center;
      }

      .logo {
        color: #C00000;
        font-weight: bold;
        font-size: 20px;
        margin-bottom: 10px;
      }

      h1 {
        margin-bottom: 25px;
        color: #004d99;
        font-size: 22px;
      }

      label {
        font-weight: bold;
        display: block;
        text-align: left;
        margin-bottom: 8px;
      }

      input[type="text"],
      input[type="number"],
      select {
        width: 100%;
        padding: 10px;
        font-size: 15px;
        border-radius: 6px;
        border: 1px solid #ccc;
        margin-bottom: 20px;
        box-sizing: border-box;
      }

      button {
        background-color: #C00000; /* RHB red color */
        color: #fff;
        padding: 10px 20px;
        font-size: 15px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.3s ease;
        width: 100%;
      }

      button:hover {
        background-color: #A00000;
      }

      .error {
        color: #C00000;
        margin-bottom: 15px;
        background-color: #FFEEEE;
        padding: 10px;
        border-radius: 6px;
        text-align: left;
      }
    </style>
  </head>
  <body>
    <div class="form-box">
      <div class="logo">RHB BANK</div>
      <h1>{{ translations[selected_lang].title }}</h1>

      {% if error %}
      <p class="error">{{ error }}</p>
      {% endif %}
      
      <form method="POST">
        <label for="customer_id">{{ translations[selected_lang].customer_id }}:</label>
        <input type="number" name="customer_id" id="customer_id" required />

        <label for="lang">{{ translations[selected_lang].select_language }}:</label>
        <select name="lang" id="lang" onchange="this.form.submit()">
          {% for code, lang_data in translations.items() %}
            <option value="{{ code }}" {% if selected_lang == code %}selected{% endif %}>
              {{ lang_data.display_name }}
            </option>
          {% endfor %}
        </select>

        <button type="submit">{{ translations[selected_lang].submit }}</button>
      </form>
    </div>
    
    <script>
      // Auto-submit the form when language is changed
      document.getElementById('lang').addEventListener('change', function() {
        this.form.submit();
      });
    </script>
  </body>
</html>""")

# Expanded translations
TRANSLATIONS = {
    'en': {
        'title': "RHB Credit Card Statement",
        'name': "Name",
        'email': "Email",
        'card_number': "Card Number",
        'statement_date': "Statement Date",
        'transaction_summary': "Transaction Summary",
        'date': "Date",
        'merchant': "Merchant",
        'category': "Category",
        'description': "Description",
        'amount': "Amount (MYR)",
        'total': "Total",
        'select_language': "Select Language",
        'submit': "Generate Statement",
        'customer_id': "Customer ID",
        'date_format': '%Y-%m-%d',
        'currency_symbol': 'MYR ',
        'footer_text': "This is a computer-generated statement and does not require a signature.",
        'display_name': "English"
    },
    'ms': {
        'title': "Penyata Kad Kredit RHB",
        'name': "Nama",
        'email': "Emel",
        'card_number': "Nombor Kad",
        'statement_date': "Tarikh Penyata",
        'transaction_summary': "Ringkasan Transaksi",
        'date': "Tarikh",
        'merchant': "Peniaga",
        'category': "Kategori",
        'description': "Keterangan",
        'amount': "Jumlah (MYR)",
        'total': "Jumlah",
        'select_language': "Pilih Bahasa",
        'submit': "Jana Penyata",
        'customer_id': "ID Pelanggan",
        'date_format': '%d-%m-%Y',
        'currency_symbol': 'RM ',
        'footer_text': "Ini adalah penyata yang dijana komputer dan tidak memerlukan tandatangan.",
        'display_name': "Bahasa Melayu"
    },
    'zh': {
        'title': "RHB信用卡对账单",
        'name': "姓名",
        'email': "电子邮件",
        'card_number': "卡号",
        'statement_date': "对账单日期",
        'transaction_summary': "交易摘要",
        'date': "日期",
        'merchant': "商家",
        'category': "类别",
        'description': "描述",
        'amount': "金额 (MYR)",
        'total': "总计",
        'select_language': "选择语言",
        'submit': "生成对账单",
        'customer_id': "客户ID",
        'date_format': '%Y年%m月%d日',
        'currency_symbol': '马币 ',
        'footer_text': "这是计算机生成的对账单，无需签名。",
        'display_name': "中文"
    },
    'ta': {
        'title': "RHB கடன் அட்டை அறிக்கை",
        'name': "பெயர்",
        'email': "மின்னஞ்சல்",
        'card_number': "அட்டை எண்",
        'statement_date': "அறிக்கை தேதி",
        'transaction_summary': "பரிவர்த்தனை சுருக்கம்",
        'date': "தேதி",
        'merchant': "வணிகர்",
        'category': "வகை",
        'description': "விளக்கம்",
        'amount': "தொகை (MYR)",
        'total': "மொத்தம்",
        'select_language': "மொழியைத் தேர்ந்தெடுக்கவும்",
        'submit': "அறிக்கையை உருவாக்கு",
        'customer_id': "வாடிக்கையாளர் ID",
        'date_format': '%d-%m-%Y',
        'currency_symbol': 'RM ',
        'footer_text': "இது கணினி உருவாக்கிய அறிக்கை மற்றும் கையொப்பம் தேவையில்லை.",
        'display_name': "தமிழ்"
    }
}

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kutty@CHITHU',
    'database': 'rhb'
}

# ========== Date Formatting ==========


def format_date(date_obj, lang):
    """Format date according to language preference"""
    date_format = TRANSLATIONS[lang]['date_format']
    if lang == 'zh':
        # Special handling for Chinese date format
        return date_obj.strftime(date_format)
    elif lang == 'ta':
        # Special handling for Tamil date format
        return date_obj.strftime(date_format)
    else:
        return date_obj.strftime(date_format)

# ========== DB Query ==========


def fetch_customer_transactions(customer_id):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute(
        "SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        raise Exception("Customer not found.")

    cursor.execute(
        "SELECT * FROM accounts WHERE customer_id = %s", (customer_id,))
    account = cursor.fetchone()
    if not account:
        raise Exception("No account found for this customer.")

    cursor.execute("""
        SELECT * FROM transactions
        WHERE account_id = %s
        ORDER BY transaction_date DESC
    """, (account['account_id'],))
    transactions = cursor.fetchall()

    cursor.close()
    conn.close()

    return customer, account, transactions

# ========== PDF Generation ==========


def generate_pdf(customer, account, transactions, lang='en'):
    # Default to English if the requested language is not available
    if lang not in TRANSLATIONS:
        lang = 'en'

    t = TRANSLATIONS[lang]

    # Calculate total amount
    total_amount = sum(tx['amount'] for tx in transactions)

    # Set appropriate font based on language
    font_family = "Arial, sans-serif"
    if lang == 'zh':
        font_family = "'Noto Sans SC', Arial, sans-serif"
    elif lang == 'ta':
        font_family = "'Noto Sans Tamil', Arial, sans-serif"

    html_template = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&family=Noto+Sans+Tamil&display=swap');
            body { 
                font-family: {{ font_family }}; 
                margin: 30px;
                direction: {{ 'rtl' if lang == 'ar' else 'ltr' }};
            }
            h1, h2 { color: #C00000; }  /* RHB red color */
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
            th { background-color: #f2f2f2; }
            .header { margin-bottom: 30px; }
            .logo { text-align: {{ 'right' if lang == 'ar' else 'left' }}; margin-bottom: 20px; }
            .info-block { margin-bottom: 5px; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; text-align: center; }
            .amount { text-align: right; }
            .total-row { font-weight: bold; background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <div class="logo">
            <h1>{{ t.title }}</h1>
        </div>
        
        <div class="header">
            <div class="info-block"><strong>{{ t.name }}:</strong> {{ customer.full_name }}</div>
            <div class="info-block"><strong>{{ t.email }}:</strong> {{ customer.email }}</div>
            <div class="info-block"><strong>{{ t.card_number }}:</strong> **** **** **** {{ account.card_number[-4:] }}</div>
            <div class="info-block"><strong>{{ t.statement_date }}:</strong> {{ statement_date }}</div>
        </div>

        <h2>{{ t.transaction_summary }}</h2>
        <table>
            <thead>
                <tr>
                    <th>{{ t.date }}</th>
                    <th>{{ t.merchant }}</th>
                    <th>{{ t.category }}</th>
                    <th>{{ t.description }}</th>
                    <th>{{ t.amount }}</th>
                </tr>
            </thead>
            <tbody>
                {% for tx in transactions %}
                <tr>
                    <td>{{ format_date(tx.transaction_date, lang) }}</td>
                    <td>{{ tx.merchant_name }}</td>
                    <td>{{ tx.category }}</td>
                    <td>{{ tx.description }}</td>
                    <td class="amount">{{ t.currency_symbol }}{{ "%.2f"|format(tx.amount) }}</td>
                </tr>
                {% endfor %}
                <tr class="total-row">
                    <td colspan="4">{{ t.total }}</td>
                    <td class="amount">{{ t.currency_symbol }}{{ "%.2f"|format(total_amount) }}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="footer">
            {{ t.footer_text }}
        </div>
    </body>
    </html>
    """
    template = Template(html_template)
    html_out = template.render(
        customer=customer,
        account=account,
        transactions=transactions,
        statement_date=format_date(datetime.now(), lang),
        t=t,
        total_amount=total_amount,
        format_date=format_date,
        lang=lang,
        font_family=font_family
    )

    filename = f"statement_customer_{customer['customer_id']}_{lang}.pdf"
    HTML(string=html_out).write_pdf(filename)
    return filename

# ========== Flask Routes ==========


@app.route('/', methods=['GET', 'POST'])
def index():
    # Get saved language preference or default to English
    lang = session.get('language', 'en')

    if request.method == 'POST':
        # Check if it's just a language change
        if 'customer_id' not in request.form or not request.form.get('customer_id'):
            lang = request.form.get('lang', 'en')
            session['language'] = lang
            return render_template('index.html',
                                   translations=TRANSLATIONS,
                                   selected_lang=lang)

        customer_id = request.form.get('customer_id')
        lang = request.form.get('lang', 'en')

        # Save language preference
        session['language'] = lang

        try:
            customer_id = int(customer_id)
            customer, account, transactions = fetch_customer_transactions(
                customer_id)

            if not transactions:
                return render_template('index.html',
                                       error="No transactions found.",
                                       translations=TRANSLATIONS,
                                       selected_lang=lang)

            pdf_file = generate_pdf(customer, account, transactions, lang)
            return send_file(pdf_file, as_attachment=True)

        except ValueError:
            return render_template('index.html',
                                   error="Invalid customer ID.",
                                   translations=TRANSLATIONS,
                                   selected_lang=lang)
        except Exception as e:
            return render_template('index.html',
                                   error=str(e),
                                   translations=TRANSLATIONS,
                                   selected_lang=lang)

    return render_template('index.html',
                           translations=TRANSLATIONS,
                           selected_lang=lang)


# ========== Start App ==========
if __name__ == '__main__':
    app.run(debug=True)
