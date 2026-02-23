import pytest
from unittest.mock import patch, MagicMock
from src.notifier import send_alert

# We patch smtplib and os.getenv where they are used inside notifier.py
@patch('src.notifier.smtplib.SMTP_SSL')
@patch('src.notifier.os.getenv')
def test_send_alert_success(mock_getenv, mock_smtp_ssl_class):
    # 1. Provide fake environment variables so the function doesn't exit early
    def mock_env(key):
        if key == "EMAIL_USER": return "fake_bot@gmail.com"
        if key == "EMAIL_PASS": return "super_secret_password"
        return None
    mock_getenv.side_effect = mock_env
    
    # 2. Setup the fake SMTP server context manager (the 'with' block)
    mock_smtp_instance = MagicMock()
    mock_smtp_ssl_class.return_value.__enter__.return_value = mock_smtp_instance
    
    # 3. Run the function
    test_message = "✅ TEST: Strategy triggered!"
    send_alert(test_message)
    
    # 4. Assertions: Verify the bot tried to log in and send the email
    mock_smtp_instance.login.assert_called_once_with("fake_bot@gmail.com", "super_secret_password")
    
    # Verify send_message was called at least once
    assert mock_smtp_instance.send_message.called
    
    # Dig into the actual email object that was sent to verify the content
    sent_email_object = mock_smtp_instance.send_message.call_args[0][0]
    assert sent_email_object['Subject'] == '!! ALGO TRADING ALERT !!'
    assert sent_email_object['To'] == 'fake_bot@gmail.com'