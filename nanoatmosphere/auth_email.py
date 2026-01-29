import os, random, smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.environ["NANO_SMTP_EMAIL"]
SENDER_PASS  = os.environ["NANO_SMTP_PASS"]  # Gmail app password

def generate_otp() -> str:
    return "{:06d}".format(random.randint(0, 999999))

def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Kalam NanoAtmosphere OTP"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    msg.set_content(f"""
        <html>
          <body style="margin:0;padding:0;background-color:#f3f5f7;font-family:Segoe UI, Arial,sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f5f7;padding:24px 0;">
              <tr>
                <td align="center">
                  <table width="480" cellpadding="0" cellspacing="0" 
                         style="background-color:#ffffff;border-radius:12px;
                                box-shadow:0 8px 24px rgba(0,0,0,0.12);overflow:hidden;">
                    <!-- Header -->
                    <tr>
                      <td style="background:#05111f;padding:18px 24px;
                                 color:#ffd54a;font-weight:700;font-size:26px;
                                 letter-spacing:1px;">
                        <span style="color:#F46DC3;">KALAM</span> NANO <span style="color:#57e0ff;">ATMOSPHERE</span>
                      </td>
                    </tr>

                    <!-- Greeting -->
                    <tr>
                      <td style="padding:22px 24px 8px 24px;font-size:15px;color:#1c2430;">
                        Hello <span style="font-weight:600;">User</span>,
                      </td>
                    </tr>

                    <!-- Body text -->
                    <tr>
                      <td style="padding:4px 24px 4px 24px;font-size:14px;line-height:1.6;color:#2c3442;">
                        Thank you for choosing Kalam NanoAtmosphere.
                        Use this One‑Time Password (OTP) to securely access your control station.
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:4px 24px 4px 24px;font-size:14px;line-height:1.6;color:#2c3442;">
                        This OTP helps verify your identity before you enter the
                        Kalam NanoAtmosphere dashboard.
                      </td>
                    </tr>

                    <!-- Warning -->
                    <tr>
                      <td style="padding:10px 24px 4px 24px;font-size:13px;line-height:1.6;
                                 color:#b53b3f;background:#fff7f5;">
                        <span style="font-weight:600;">Security reminder:</span>
                        Never share this OTP with anyone, even if they claim to be from Kalam NanoAtmosphere.
                      </td>
                    </tr>

                    <!-- OTP pill -->
                    <tr>
                      <td align="center" style="padding:26px 24px 10px 24px;">
                        <div style="display:inline-block;background:#004a7c;color:#ffffff;
                                    font-size:24px;font-weight:700;letter-spacing:3px;
                                    border-radius:8px;padding:12px 32px;">
                          {otp}
                        </div>
                      </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                      <td style="padding:10px 24px 4px 24px;font-size:13px;color:#5a6475;">
                        Regards,
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:0 24px 24px 24px;font-size:13px;color:#5a6475;">
                        Team Kalam Nanoatmosphere
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """,subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.send_message(msg)
