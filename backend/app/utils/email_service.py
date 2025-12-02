import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Récupération des variables d'environnement
SMTP_SERVER = os.getenv("SMTP_SERVER")
try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
except ValueError:
    SMTP_PORT = 587
    
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# --- MODIFICATION DE LA SIGNATURE ICI ---
def send_agent_welcome_email(to_email: str, login_email: str, first_name: str, temp_password: str):
    """
    Envoie un email de bienvenue.
    to_email    : Adresse de destination (Email Perso)
    login_email : Identifiant à afficher (Email Pro)
    """
    if not SMTP_SERVER or not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️ Configuration Email incomplète.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL or SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = "Bienvenue sur FraudDetect - Vos accès Agent"

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
              <h2 style="color: #10b981;">Bienvenue, {first_name} !</h2>
              <p>Votre compte Agent sur la plateforme <strong>FraudDetect</strong> a été créé avec succès.</p>
              
              <p>Voici vos identifiants temporaires pour votre première connexion :</p>
              
              <div style="background-color: #f4f4f5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #666;">Identifiant (Email Pro) :</p>
                <p style="margin: 5px 0; font-weight: bold; font-size: 16px;">{login_email}</p>
                <br/>
                <p style="margin: 0; font-size: 14px; color: #666;">Mot de passe temporaire :</p>
                <p style="margin: 5px 0; font-weight: bold; font-size: 18px; color: #10b981; font-family: monospace;">{temp_password}</p>
              </div>

              <p><strong>Action requise :</strong> Connectez-vous dès maintenant pour changer ce mot de passe.</p>
              
              <a href="http://localhost:5173/auth" style="display: inline-block; background-color: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Accéder à la plateforme</a>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email envoyé avec succès à {to_email}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        return False