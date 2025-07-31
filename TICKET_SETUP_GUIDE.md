# Ticket System Setup Guide

The ticket system works for **one server only** with all configuration stored in a JSON file. **No slash commands are available** - everything is configured by manually editing the JSON file. The ticket panel will automatically be sent to the configured channel when the bot starts.

## Configuration Steps

### 1. Edit the Configuration File
Open `ticket/config/ticket_config.json` and replace the placeholder values with your actual Discord IDs:

```json
{
  "server_id": "YOUR_SERVER_ID_HERE",
  "ticket_channel_id": "YOUR_TICKET_CHANNEL_ID_HERE", 
  "staff_role_id": "YOUR_STAFF_ROLE_ID_HERE",
  "category_id": "YOUR_CATEGORY_ID_HERE",
  "panel_embed_data": {
    "content": null,
    "embeds": [
      {
        "title": "🎟️ Clan Application",
        "description": "Click the button below to create a ticket for clan application.\n\nPlease have your player tag ready!",
        "color": 3447003,
        "footer": {
          "text": "Make sure you're eligible before applying!"
        },
        "thumbnail": {
          "url": "https://i.imgur.com/your-image.png"
        }
      }
    ]
  },
  "welcome_embed_data": {
    "content": "Welcome to our clan application system!",
    "embeds": [
      {
        "title": "🎉 Welcome to Clan Application",
        "description": "Thank you for your interest in joining our clan!\n\nYour application ticket has been created and our staff team will review it shortly.\n\n**What happens next?**\n• Staff will review your profile\n• You may be asked additional questions\n• We'll make a decision within 24 hours\n\n**Need help?** Feel free to ask any questions here!",
        "color": 65280,
        "footer": {
          "text": "Please be patient while we review your application"
        }
      }
    ]
  },
  "button_label": "🎟️ Apply to Clan",
  "button_color": "primary"
}
```

### 2. How to Get Discord IDs

To get the required IDs, enable Developer Mode in Discord (Settings → Advanced → Developer Mode), then:

- **Server ID**: Right-click on your server name → Copy Server ID
- **Channel ID**: Right-click on the ticket channel → Copy Channel ID  
- **Role ID**: Right-click on the staff role → Copy Role ID
- **Category ID**: Right-click on the tickets category → Copy Category ID

### 3. Customize Embeds (Optional)

The JSON file now includes comprehensive sample embeds with all available Discord embed features. You can customize the `panel_embed_data` and `welcome_embed_data` sections:

**Basic Properties:**
- **title**: The embed title
- **description**: Main embed text (supports Discord markdown)
- **color**: Decimal color code (use a color picker and convert to decimal)
- **content**: Text that appears above the embed (can be null)

**Advanced Properties:**
- **footer.text**: Small text at the bottom
- **footer.icon_url**: Small icon next to footer text
- **thumbnail.url**: Small image in top-right corner
- **image.url**: Large image at the bottom
- **author.name**: Author name at the top
- **author.icon_url**: Small icon next to author name
- **fields**: Array of field objects with name, value, and inline properties
- **timestamp**: ISO timestamp for embed (shows "Today at X:XX PM")

**Field Structure:**
```json
{
  "name": "Field Title",
  "value": "Field content",
  "inline": true
}
```

**Color Examples:**
- Red: 16711680
- Green: 65280  
- Blue: 255
- Orange: 16744192
- Purple: 10181046
- Gold: 16766720

### 4. Button Customization

- **button_label**: Text on the ticket creation button
- **button_color**: `primary` (blue), `success` (green), `danger` (red), or `secondary` (gray)

## Automatic Features

- **Auto Panel Send**: When the bot starts, it automatically sends the ticket panel to the configured channel
- **Single Server**: All configuration is stored in the JSON file for one server only
- **No Commands**: No slash commands - all configuration is done via JSON file editing
- **No Database Required**: MongoDB is no longer needed - everything uses JSON files

## Important Notes

- **Configure ALL required IDs before starting the bot** for automatic panel posting
- If any required setting is missing, the panel won't be sent automatically
- The bot will print status messages about panel sending in the console
- The system maintains all existing ticket functionality (user creation, staff management, etc.)
- Make sure the bot has permissions in the configured channel and category
- Backup your configuration file before making changes

## Troubleshooting

- **Panel not sent on startup**: Check that all IDs in the JSON are correct and not placeholder values
- **Bot can't find server/channel**: Verify the IDs are correct and the bot has access
- **Staff role not working**: Ensure the role ID is correct and the bot can see the role
- **Category issues**: Make sure the category exists and the bot can create channels in it