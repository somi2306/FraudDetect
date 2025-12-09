import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Récupération des variables d'environnement
SMTP_SERVER = os.getenv("SMTP_SERVER")
try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
except (ValueError, TypeError):
    SMTP_PORT = 587
    
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def _send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Fonction helper interne pour l'envoi SMTP"""
    if not SMTP_SERVER or not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️ Configuration Email incomplète (SMTP). L'email n'a pas été envoyé.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL or SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email envoyé avec succès à {to_email}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email à {to_email} : {e}")
        return False

def send_agent_welcome_email(to_email: str, login_email: str, first_name: str, temp_password: str):
    """
    Envoie un email de bienvenue (Création de compte).
    """
    subject = "Bienvenue sur FraudDetect - Vos accès Agent"
    
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
    return _send_email(to_email, subject, html_content)

def send_password_reset_email(to_email: str, login_email: str, first_name: str, temp_password: str):
    """
    Envoie un email spécifique pour la réinitialisation de mot de passe (Admin).
    """
    subject = "Réinitialisation de votre mot de passe - FraudDetect"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
          <h2 style="color: #eab308;">Réinitialisation de mot de passe</h2>
          <p>Bonjour {first_name},</p>
          <p>Un administrateur a demandé la réinitialisation de votre mot de passe sur la plateforme <strong>FraudDetect</strong>.</p>
          
          <div style="background-color: #fefce8; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; border: 1px solid #fef9c3;">
            <p style="margin: 0; font-size: 14px; color: #666;">Identifiant :</p>
            <p style="margin: 5px 0; font-weight: bold; font-size: 16px;">{login_email}</p>
            <br/>
            <p style="margin: 0; font-size: 14px; color: #666;">Nouveau mot de passe temporaire :</p>
            <p style="margin: 5px 0; font-weight: bold; font-size: 18px; color: #eab308; font-family: monospace;">{temp_password}</p>
          </div>

          <p><strong>Action requise :</strong> Connectez-vous dès maintenant pour définir votre propre mot de passe.</p>
          
          <a href="http://localhost:5173/auth" style="display: inline-block; background-color: #eab308; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Se connecter</a>
          
          <p style="font-size: 12px; color: #999; margin-top: 30px;">
            Si vous n'êtes pas à l'origine de cette demande, veuillez contacter votre administrateur immédiatement.
          </p>
        </div>
      </body>
    </html>
    """
    return _send_email(to_email, subject, html_content)

def send_account_status_email(to_email: str, first_name: str, is_active: bool):
    """
    Notifie l'agent d'un changement de statut (Activé/Désactivé).
    """
    status_text = "ACTIVÉ" if is_active else "DÉSACTIVÉ"
    color = "#10b981" if is_active else "#ef4444" 
    subject = f"Mise à jour de votre compte Agent - {status_text}"

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
          <h2>Bonjour {first_name},</h2>
          <p>Le statut de votre compte Agent sur <strong>FraudDetect</strong> a été modifié par un administrateur.</p>
          
          <div style="background-color: #f4f4f5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
            <p style="margin: 0; font-size: 14px; color: #666;">Nouveau statut :</p>
            <p style="margin: 5px 0; font-weight: bold; font-size: 18px; color: {color};">
                {status_text}
            </p>
          </div>

          <p>
            { "Vous pouvez à nouveau accéder à la plateforme avec vos identifiants habituels." if is_active else "Votre accès a été temporairement suspendu. Veuillez contacter l'administrateur pour plus d'informations." }
          </p>
        </div>
      </body>
    </html>
    """
    return _send_email(to_email, subject, html_content)