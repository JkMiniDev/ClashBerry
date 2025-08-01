# Ticket System Configuration

## Setup Instructions

1. **Configure ticket_config.json:**
   - Set your `server_id`
   - Set your `staff_role_id` 
   - Set your `ticket_category_id`

2. **Configure Embed Files:**
   - **Panel Embed:** Edit `commands/embeds/panel.json` for ticket panel appearance
   - **Welcome Embed:** Edit `commands/embeds/welcome.json` for welcome message in tickets

3. **Sending Ticket Panels:**
   - **Mention the bot** and type "post" to send ticket panels
   - **Admin permissions required** - only administrators can use this
   - **Syntax:** `@BotName post [#channel]`
   - If no channel is mentioned, panel sends to current channel
   - If channel is mentioned, panel sends to that channel

## Configuration Files

### Server Configuration (`ticket_config.json`)
```json
{
  "server_id": "YOUR_SERVER_ID_HERE",
  "staff_role_id": "YOUR_STAFF_ROLE_ID_HERE", 
  "ticket_category_id": "YOUR_TICKET_CATEGORY_ID_HERE"
}
```

### Panel Embed (`commands/embeds/panel.json`)
```json
{
  "title": "🎫 Ticket System",
  "description": "Click the button below to create a new ticket.",
  "color": 5763719,
  "thumbnail": {"url": ""},
  "footer": {"text": "Ticket System", "icon_url": ""},
  "button": {"label": "🎟️ Create Ticket", "color": "primary"}
}
```

### Welcome Embed (`commands/embeds/welcome.json`)
```json
{
  "title": "Welcome to Your Ticket",
  "description": "Thank you for creating a ticket! A staff member will be with you shortly.",
  "color": 3066993,
  "footer": {"text": "Support Team", "icon_url": ""}
}
```

## Usage Examples

- `@BotName post` - Sends panel to current channel
- `@BotName post #tickets` - Sends panel to #tickets channel
- `@BotName post #general` - Sends panel to #general channel

## Features

- ✅ Admin-only mention command (silent ignore for non-admins)
- ✅ Optional channel targeting
- ✅ Separated embed configuration files
- ✅ Dropdown account selection for tickets
- ✅ Multi-account support

## Notes

- Server details in main config file
- Embed designs in separate JSON files for easy customization
- Bot validates permissions before sending panels
- No slash commands needed - just mention the bot with "post"
