# Ticket System Configuration

## Setup Instructions

1. **Configure ticket_config.json:**
   - Set your `server_id`
   - Set your `staff_role_id` 
   - Set your `ticket_category_id`
   - `ticket_channel_id` is now optional (used for legacy compatibility)

2. **Sending Ticket Panels:**
   - Use the `/sendpanel` slash command to send ticket panels
   - **Admin permissions required** - only administrators can use this command
   - **Syntax:** `/sendpanel [channel]`
   - If no channel is mentioned, panel sends to current channel
   - If channel is mentioned, panel sends to that channel

## Usage Examples

- `/sendpanel` - Sends panel to current channel
- `/sendpanel #tickets` - Sends panel to #tickets channel
- `/sendpanel channel:general` - Sends panel to #general channel

## Features

- ✅ Admin-only command (silent ignore for non-admins)
- ✅ Optional channel targeting
- ✅ Permission validation
- ✅ Dropdown account selection for tickets
- ✅ Multi-account support

## Notes

- Bot no longer sends panels automatically on startup
- Only users with Administrator permission can send panels
- Non-admin users will receive no response (silent ignore)
- Bot validates permissions before sending panels
