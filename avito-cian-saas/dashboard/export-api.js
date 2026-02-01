// Export API for Avito-CIAN Parser SaaS
// Handles Gmail, Google Sheets, and Telegram exports

class ExportAPI {
    constructor() {
          this.userSettings = this.loadUserSettings();
    }

  loadUserSettings() {
        const saved = localStorage.getItem('exportSettings');
        return saved ? JSON.parse(saved) : {};
  }

  saveUserSettings(settings) {
        this.userSettings = { ...this.userSettings, ...settings };
        localStorage.setItem('exportSettings', JSON.stringify(this.userSettings));
  }

  // Format data for export
  formatDataForExport(data) {
        return {
                price: data.price || 'N/A',
                address: data.address || 'N/A',
                area: data.area || 'N/A',
                photos: data.photos || [],
                contacts: data.contacts || 'N/A',
                link: data.link || 'N/A',
                timestamp: new Date().toISOString()
        };
  }

  // Export to Gmail via EmailJS
  async exportToGmail(data, userEmail) {
        if (!userEmail) {
                alert('Please enter your email address');
                return false;
        }

      const formattedData = this.formatDataForExport(data);
        const emailContent = this.generateEmailContent(formattedData);

      // Using EmailJS service (free tier available)
      // Requires: https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/index.min.js
      try {
              await emailjs.send('service_id', 'template_id', {
                        to_email: userEmail,
                        subject: 'Avito/CIAN Parser Results',
                        message: emailContent,
                        reply_to: userEmail
              });
              return true;
      } catch (error) {
              console.error('Email send failed:', error);
              return false;
      }
  }

  // Export to Google Sheets
  async exportToGoogleSheets(data, sheetUrl, authToken) {
        const formattedData = this.formatDataForExport(data);

      try {
              // Extract Sheet ID from URL
          const sheetId = this.extractSheetId(sheetUrl);

          const response = await fetch(
                    `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/A1:append?valueInputOption=USER_ENTERED&key=${authToken}`,
            {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                                      values: [[
                                                      formattedData.price,
                                                      formattedData.address,
                                                      formattedData.area,
                                                      formattedData.contacts,
                                                      formattedData.link,
                                                      formattedData.timestamp
                                                    ]]
                        })
            }
                  );

          return response.ok;
      } catch (error) {
              console.error('Google Sheets export failed:', error);
              return false;
      }
  }

  // Export to Telegram
  async exportToTelegram(data, botToken, chatId) {
        const formattedData = this.formatDataForExport(data);
        const message = this.generateTelegramMessage(formattedData);

      try {
              const response = await fetch(
                        `https://api.telegram.org/bot${botToken}/sendMessage`,
                {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                          chat_id: chatId,
                                          text: message,
                                          parse_mode: 'HTML'
                            })
                }
                      );

          return response.ok;
      } catch (error) {
              console.error('Telegram export failed:', error);
              return false;
      }
  }

  // Generate email content
  generateEmailContent(data) {
        return `
              <h2>Parser Results</h2>
                    <p><strong>Price:</strong> ${data.price}</p>
                          <p><strong>Address:</strong> ${data.address}</p>
                                <p><strong>Area:</strong> ${data.area} м²</p>
                                      <p><strong>Contacts:</strong> ${data.contacts}</p>
                                            <p><strong>Link:</strong> <a href="${data.link}">${data.link}</a></p>
                                                  <p><em>Generated: ${data.timestamp}</em></p>
                                                      `;
  }

  // Generate Telegram message
  generateTelegramMessage(data) {
        return `
        <b>🏠 Parser Results</b>
        <b>💰 Price:</b> ${data.price}
        <b>📍 Address:</b> ${data.address}
        <b>📐 Area:</b> ${data.area} м²
        <b>📱 Contacts:</b> ${data.contacts}
        <b>🔗 Link:</b> <a href="${data.link}">View Listing</a>
        <i>⏰ ${data.timestamp}</i>
            `;
  }

  // Extract Sheet ID from URL
  extractSheetId(url) {
        const match = url.match(/\/d\/(.*?)\//);
        return match ? match[1] : null;
  }

  // CSV export
  exportToCSV(data, filename = 'export.csv') {
        const formattedData = this.formatDataForExport(data);
        const csv = `Price,Address,Area,Contacts,Link\n${formattedData.price},${formattedData.address},${formattedData.area},${formattedData.contacts},${formattedData.link}`;

      const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
  }
}

// Initialize global export API
const exportAPI = new ExportAPI();
