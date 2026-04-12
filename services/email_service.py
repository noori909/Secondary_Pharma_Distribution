import smtplib
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.database import SessionLocal
from data.models import Sale

# ── Credentials ────────────────────────────────────────────────────────────
SENDER_EMAIL    = "newquettamedicalandsurgical@gmail.com"
SENDER_PASSWORD = "cdnh ctfc eoqk tikj"
RECEIVER_EMAIL  = "raeesnomanbaloch@gmail.com"
CC_EMAILS       = ["vitaleaseofficial@gmail.com", "dr.maqbooljabbar@gmail.com"]


def send_daily_report():
    """Compile today's sales stats and email an HTML report to the Boss + CC list."""
    session = SessionLocal()
    try:
        today = datetime.now().date()

        cash_sales = session.query(Sale).filter(
            Sale.date == today,
            Sale.payment_status == 'cash'
        ).all()
        daily_cash  = sum(s.net_amount for s in cash_sales)
        cash_count  = len(cash_sales)

        credit_sales = session.query(Sale).filter(
            Sale.date == today,
            Sale.payment_status == 'credit'
        ).all()
        daily_credit  = sum(s.net_amount for s in credit_sales)
        credit_count  = len(credit_sales)


    except Exception as e:
        print(f"Failed to query daily stats: {e}")
        return False
    finally:
        session.close()

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px; background:#f9f9f9;">
        <div style="max-width:560px; margin:auto; background:#fff; border-radius:8px;
                    box-shadow:0 2px 8px rgba(0,0,0,.1); overflow:hidden;">
          <div style="background:#2c3e50; padding:20px;">
            <h2 style="color:#fff; margin:0;">New Quetta Surgical &amp; Medicine Distributors</h2>
            <p style="color:#bdc3c7; margin:4px 0 0;">Automated Daily Report &mdash; {today.strftime('%A, %d %B %Y')}</p>
          </div>
          <div style="padding:24px;">
            <table width="100%" border="1" cellpadding="10" style="border-collapse:collapse; font-size:14px;">
              <tr style="background:#2980b9; color:#fff;">
                <th align="left">Metric</th>
                <th align="right">Amount (Rs.)</th>
                <th align="center">Invoices</th>
              </tr>
              <tr>
                <td><b>Cash Collected (Paid)</b></td>
                <td align="right" style="color:#27ae60;"><b>Rs. {daily_cash:,.2f}</b></td>
                <td align="center">{cash_count}</td>
              </tr>
              <tr style="background:#fdf7f7;">
                <td><b>Credit Pending (Unpaid)</b></td>
                <td align="right" style="color:#c0392b;"><b>Rs. {daily_credit:,.2f}</b></td>
                <td align="center">{credit_count}</td>
              </tr>
              <tr style="background:#eaf4fb;">
                <td><i>Gross Revenue (Cash + Credit)</i></td>
                <td align="right"><i>Rs. {daily_cash + daily_credit:,.2f}</i></td>
                <td align="center">{cash_count + credit_count}</td>
              </tr>
            </table>
          </div>
          <div style="background:#ecf0f1; padding:14px 24px; font-size:12px; color:#7f8c8d;">
            This is an automated end-of-day summary sent securely from the Pharma Distribution System.<br>
            A timestamped database backup has also been uploaded to Google Drive simultaneously.
          </div>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Daily Store Report — New Quetta ({today.strftime('%d %b %Y')})"
    msg['From']    = f"New Quetta Pharma System <{SENDER_EMAIL}>"
    msg['To']      = RECEIVER_EMAIL
    msg['Cc']      = ", ".join(CC_EMAILS)
    msg.attach(MIMEText(html, 'html'))

    all_recipients = [RECEIVER_EMAIL] + CC_EMAILS

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, all_recipients, msg.as_string())
        server.quit()
        print(f"Daily report emailed to {all_recipients}")
        return True
    except Exception as e:
        print(f"SMTP error: {e}")
        return False
