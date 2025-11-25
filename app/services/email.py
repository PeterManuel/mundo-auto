import smtplib
import logging
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "mundoauto2025@gmail.com"
        # IMPORTANT: You need to set up a Gmail App Password
        # 1. Go to Google Account settings (myaccount.google.com)
        # 2. Security -> 2-Step Verification -> App passwords
        # 3. Generate a new app password for 'Mail'
        # 4. Replace this with your actual 16-character app password
        self.password = "mowu aemc gegx bfuj"  # REPLACE THIS with Gmail App Password
    
    def _create_connection(self):
        """Create SMTP connection"""
        try:
            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            logger.info(f"Attempting to login with email: {self.email}")
            server.login(self.email, self.password)
            logger.info("SMTP connection established successfully")
            return server
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            logger.error("Make sure you're using a Gmail App Password, not your regular password")
            raise
        except Exception as e:
            logger.error(f"Failed to create email connection: {str(e)}")
            raise
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email with HTML content"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email
            message["To"] = to_email
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with self._create_connection() as server:
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str = None):
        """Send password reset email"""
        reset_url = f"{settings.BACKEND_CORS_ORIGINS[0]}/reset-password?token={reset_token}"
        
        # HTML template for password reset email
        html_template = Template("""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperación de Contraseña - MundoAuto</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }
                .header { 
                    background-color: #2563eb; 
                    color: white; 
                    padding: 20px; 
                    text-align: center; 
                    border-radius: 8px 8px 0 0; 
                }
                .content { 
                    background-color: #f8fafc; 
                    padding: 30px; 
                    border: 1px solid #e2e8f0; 
                }
                .button { 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #2563eb; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 6px; 
                    margin: 20px 0; 
                }
                .footer { 
                    background-color: #64748b; 
                    color: white; 
                    padding: 15px; 
                    text-align: center; 
                    font-size: 12px; 
                    border-radius: 0 0 8px 8px; 
                }
                .warning { 
                    background-color: #fef3c7; 
                    border-left: 4px solid #f59e0b; 
                    padding: 12px; 
                    margin: 20px 0; 
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚗 MundoAuto</h1>
                <h2>Recuperação de Senha</h2>
            </div>
            
            <div class="content">
                <p>Olá{% if user_name %} {{ user_name }}{% endif %},</p>
                
                <p>Recebemos uma solicitação para redefinir a senha da sua conta no MundoAuto.</p>
                
                <p>Se você solicitou esta alteração, clique no botão abaixo para criar uma nova senha:</p>
                
                <div style="text-align: center;">
                    <a href="{{ reset_url }}" class="button">Redefinir Senha</a>
                </div>
                
                <p>Ou copie e cole este link no seu navegador:</p>
                <p style="word-break: break-all; background-color: #e2e8f0; padding: 10px; border-radius: 4px;">
                    {{ reset_url }}
                </p>
                
                <div class="warning">
                    <strong>⚠️ Importante:</strong>
                    <ul>
                        <li>Este link expira em 1 hora por segurança</li>
                        <li>Se você não solicitou esta alteração, ignore este email</li>
                        <li>Nunca compartilhe este link com ninguém</li>
                    </ul>
                </div>
                
                <p>Precisa de ajuda? Entre em contato com nossa equipe de suporte.</p>
                
                <p>Atenciosamente,<br><strong>Equipe MundoAuto</strong></p>
            </div>
            
            <div class="footer">
                © 2025 MundoAuto - Sistema de E-commerce para Autopartes<br>
                Este es un correo automático, por favor no respondas a esta dirección.
            </div>
        </body>
        </html>
        """)
        
        # Text version for email clients that don't support HTML
        text_content = f"""
        MundoAuto - Recuperação de Senha
        
        Olá{f' {user_name}' if user_name else ''},
        
        Recebemos uma solicitação para redefinir a senha da sua conta no MundoAuto.
        
        Se você solicitou esta alteração, copie e cole o seguinte link no seu navegador:
        {reset_url}
        
        IMPORTANTE:
        - Este link expira em 1 hora por segurança
        - Se você não solicitou esta alteração, ignore este email
        - Nunca compartilhe este link com ninguém
        
        Precisa de ajuda? Entre em contato com nossa equipe de suporte.
        
        Atenciosamente,
        Equipe MundoAuto
        
        © 2025 MundoAuto - Este é um email automático, por favor não responda a este endereço.
        """
        
        html_content = html_template.render(
            reset_url=reset_url,
            user_name=user_name
        )
        
        return self.send_email(
            to_email=to_email,
            subject="🔐 Recuperação de Senha - MundoAuto",
            html_content=html_content,
            text_content=text_content
        )


# Create a singleton instance
email_service = EmailService()