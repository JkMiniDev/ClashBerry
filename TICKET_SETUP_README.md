# Ticket System Configuration

## Setup Instructions

1. **Configure ticket_config.json:**
   - Set your `server_id`
   - Set your `staff_role_id` 
   - Set your `ticket_category_id`

2. **Sending Ticket Panels:**
   - **Mention the bot** and type "post" to send ticket panels
   - **Admin permissions required** - only administrators can use this
   - **Syntax:** `@BotName post [#channel]`
   - If no channel is mentioned, panel sends to current channel
   - If channel is mentioned, panel sends to that channel

## Usage Examples

- `@BotName post` - Sends panel to current channel
- `@BotName post #tickets` - Sends panel to #tickets channel
- `@BotName post #general` - Sends panel to #general channel

## Features

- ✅ Admin-only mention command (silent ignore for non-admins)
- ✅ Optional channel targeting
- ✅ Permission validation
- ✅ Dropdown account selection for tickets
- ✅ Multi-account support

## Notes

- Bot no longer sends panels automatically on startup
- Only users with Administrator permission can send panels
- Non-admin users will receive no response (silent ignore)
- Bot validates permissions before sending panels
- No slash commands needed - just mention the bot with "post"
