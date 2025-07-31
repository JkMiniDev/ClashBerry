# Ticket System Setup Guide

The ticket system has been modified to work for **one server only** with all configuration stored in a JSON file. The ticket panel will automatically be sent to the configured channel when the bot starts.

## Configuration Steps

### 1. Configure Basic Settings
Use the `/ticket-settings` command to configure the basic settings:

```
/ticket-settings server_id:<YOUR_SERVER_ID> ticket_channel:<#ticket-channel> staff_role:<@staff-role> category:<ticket-category>
```

**Parameters:**
- `server_id`: Your Discord server ID (right-click server → Copy Server ID)
- `ticket_channel`: The channel where the ticket panel will be posted
- `staff_role`: The role that can manage tickets
- `category`: The category where ticket channels will be created

### 2. Configure Panel Appearance (Optional)
Use the `/ticket-panel` command to customize the ticket panel:

```
/ticket-panel panel_embed:<discohook-link> welcome_embed:<discohook-link> button_label:"🎟️ Create Ticket" button_color:primary
```

**Parameters:**
- `panel_embed`: Discohook link for the main panel embed (optional)
- `welcome_embed`: Discohook link for the welcome message in tickets (optional)
- `button_label`: Text on the ticket creation button (optional)
- `button_color`: Button color - primary/success/danger/secondary (optional)

### 3. Manual Panel Posting (Optional)
If you need to manually post the panel to a different channel:

```
/ticket-post channel:<#channel>
```

## Automatic Features

- **Auto Panel Send**: When the bot starts, it automatically sends the ticket panel to the configured channel
- **Single Server**: All configuration is stored in `ticket/config/ticket_config.json` for one server only
- **No Database Required**: MongoDB is no longer needed - everything uses JSON files

## Configuration File

The configuration is stored in `ticket/config/ticket_config.json`:

```json
{
  "server_id": "YOUR_SERVER_ID",
  "ticket_channel_id": "CHANNEL_ID_FOR_PANEL",
  "staff_role_id": "STAFF_ROLE_ID",
  "category_id": "CATEGORY_ID",
  "panel_embed_data": {...},
  "welcome_embed_data": {...},
  "button_label": "🎟️ Create Ticket",
  "button_color": "primary"
}
```

## Important Notes

- Configure the settings **before** starting the bot for automatic panel posting
- If any required setting is missing, the panel won't be sent automatically
- The bot will print status messages about panel sending in the console
- All ticket commands now work without guild_id or panel_name parameters
- The system maintains all existing ticket functionality while being simplified for single-server use