## Email Configuration

To enable email notifications:

1. Create a `.env` file in the root directory
2. Add the following email configuration:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=recruitment@yourcompany.com
   ```

For Gmail:
1. Enable 2-Step Verification
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Select "Mail" and your device
   - Use the generated password as SMTP_PASSWORD 