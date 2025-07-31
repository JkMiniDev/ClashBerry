# Single Server Ticket Bot

A Discord bot designed for managing support tickets on a single server. The bot automatically posts a ticket panel when it starts up and handles ticket creation, management, and closure.

## Features

- ✅ **Single Server Focus**: Designed for one server only
- ✅ **JSON Configuration**: No database required - all settings stored in JSON
- ✅ **Auto Panel Posting**: Automatically posts ticket panel on startup
- ✅ **Staff Role Integration**: Configurable staff role for ticket management
- ✅ **Category Organization**: Tickets created in specified category
- ✅ **Player Tag Collection**: Collects player tags when creating tickets
- ✅ **Ticket Controls**: Close tickets with reason logging
- ✅ **Custom Embeds**: Configurable panel and welcome messages

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Environment File

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_bot_token_here
```

### 3. Configure the Bot

Edit `config.json` with your server details:

```json
{
  "server_id": "YOUR_SERVER_ID_HERE",
  "ticket_channel_id": "YOUR_TICKET_CHANNEL_ID_HERE", 
  "staff_role_id": "YOUR_STAFF_ROLE_ID_HERE",
  "category_id": "YOUR_TICKET_CATEGORY_ID_HERE",
  "panel_embed": {
    "title": "🎫 Support Tickets",
    "description": "Need help? Click the button below to create a support ticket!\n\n**What happens next?**\n✅ A private channel will be created\n✅ Staff will be notified\n✅ We'll help resolve your issue",
    "color": 3447003,
    "footer": {
      "text": "Support Team • Click below to get started"
    }
  },
  "welcome_embed": {
    "title": "🎫 Ticket Created", 
    "description": "Welcome {user}! Thank you for creating a ticket.\n\n**Please provide the following information:**\n• Your in-game tag\n• Detailed description of your issue\n• Any relevant screenshots\n\nA staff member will assist you shortly!",
    "color": 65280,
    "footer": {
      "text": "Support Team"
    }
  },
  "button_label": "🎟️ Create Ticket",
  "button_color": "primary"
}
```

### 4. Get Required IDs

To find the required IDs:

1. **Server ID**: Right-click your server name → Copy Server ID
2. **Channel ID**: Right-click the channel where tickets panel should be posted → Copy Channel ID  
3. **Role ID**: Right-click the staff role → Copy Role ID
4. **Category ID**: Right-click the category where tickets should be created → Copy Category ID

> **Note**: You need to enable Developer Mode in Discord settings to see these options.

### 5. Run the Bot

```bash
python bot.py
```

## How It Works

1. **Bot Startup**: When the bot starts, it automatically posts the ticket panel to the configured channel
2. **Ticket Creation**: Users click the button to create a ticket, enter their player tag, and a private channel is created
3. **Staff Notification**: Staff members with the configured role are automatically given access to new tickets
4. **Ticket Management**: Staff can close tickets with a reason, and channels are automatically deleted after 5 seconds

## Bot Permissions Required

Make sure your bot has these permissions:

- ✅ Read Messages
- ✅ Send Messages  
- ✅ Manage Channels (to create/delete ticket channels)
- ✅ Manage Messages (to delete old panel messages)
- ✅ Embed Links
- ✅ Use Slash Commands
- ✅ Mention Everyone (to ping staff roles)

## Customization

### Button Colors
Available button colors in `config.json`:
- `primary` (blue)
- `secondary` (grey) 
- `success` (green)
- `danger` (red)

### Embed Colors
Colors in embeds are specified as decimal numbers:
- `3447003` = Blue
- `65280` = Green  
- `16711680` = Red
- `16776960` = Yellow

### Welcome Message Variables
In the welcome embed description, you can use:
- `{user}` - Mentions the user who created the ticket

## Troubleshooting

### Bot doesn't post panel on startup
- Check that `server_id` and `ticket_channel_id` are correct in config.json
- Ensure the bot has permissions in the target channel
- Check the console for error messages

### Tickets not creating properly  
- Verify `category_id` exists and bot has permissions
- Check that `staff_role_id` is valid
- Ensure bot can create channels in the category

### Configuration not loading
- Validate your `config.json` syntax using a JSON validator
- Ensure all required fields are present
- Check file permissions

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all IDs in config.json are correct
3. Ensure bot permissions are properly set
4. Make sure the bot is in your server and online