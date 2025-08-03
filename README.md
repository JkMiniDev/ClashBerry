# Clash of Clans Discord Bot Web Portal

A modern, responsive web application that showcases all Discord bot commands and provides a web interface for searching Clash of Clans clan and player data. Built with Flask and Bootstrap, this portal offers the same functionality as your Discord bot through an intuitive web interface.

## 🌟 Features

### 🏠 Web Portal
- **Modern UI**: Responsive Bootstrap 5 design with custom styling
- **Clan Search**: Comprehensive clan information, member lists, and war data
- **Player Search**: Detailed player statistics, achievements, and troop information
- **Command Showcase**: Interactive documentation of all Discord bot commands
- **Real-time Data**: Direct integration with Clash of Clans API

### 🔍 Clan Features
- Clan overview and statistics
- Complete member list with Town Hall levels
- Current war information and progress
- Clan War League (CWL) group data
- Member donation tracking
- War win statistics and streaks

### 👤 Player Features
- Comprehensive player statistics
- Achievement progress tracking
- Troop, spell, and hero levels
- League information and trophies
- Clan membership details
- Builder Hall progression

### 🗡️ War Features
- Current war status and timeline
- Attack progress tracking
- Star and destruction percentages
- CWL group standings
- War preparation details

### 🤖 Discord Commands Documentation
- Complete command reference
- Usage examples and descriptions
- Feature breakdowns for each command
- Web alternatives for Discord-only features

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Clash of Clans API token
- Git (for cloning)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies**
   ```bash
   pip install -r website_requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```bash
   API_TOKEN=your_clash_of_clans_api_token_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the website**
   Open your browser and navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
- `API_TOKEN`: Your Clash of Clans API token (required)
- `FLASK_ENV`: Set to `development` for debug mode
- `FLASK_DEBUG`: Set to `True` for auto-reload

### Getting a COC API Token
1. Visit [Clash of Clans Developer Portal](https://developer.clashofclans.com/)
2. Create an account and log in
3. Create a new key with your IP address
4. Copy the token to your `.env` file

## 📱 Usage

### Clan Search
1. Navigate to the **Clan Search** page
2. Enter a clan tag (with or without #)
3. View comprehensive clan information including:
   - Clan statistics and requirements
   - Complete member list with roles and levels
   - Current war status and progress
   - CWL group information (if available)

### Player Search
1. Go to the **Player Search** page
2. Enter a player tag (with or without #)
3. Explore detailed player data including:
   - Statistics and achievement progress
   - Troop, spell, and hero levels
   - League information and trophies
   - Current clan membership

### Discord Commands
1. Visit the **Commands** page
2. Browse all available Discord bot commands
3. View usage examples and feature descriptions
4. Access web alternatives for supported commands

## 🛠️ API Integration

The website integrates directly with the Clash of Clans API to provide:
- Real-time clan and player data
- Current war information
- Achievement and progression tracking
- League and trophy information

### API Endpoints
The website also provides its own REST API:
- `GET /api/clan/<clan_tag>` - Clan data
- `GET /api/player/<player_tag>` - Player data
- `GET /api/war/<clan_tag>` - War data

## 🎨 Customization

### Styling
- Custom CSS in `static/css/style.css`
- Bootstrap 5 components and utilities
- Responsive design for all screen sizes
- Dark mode support (automatic detection)

### Templates
- Jinja2 templates in `templates/` directory
- Base template with common layout
- Individual pages for each feature
- Modular and extensible structure

## 🚀 Deployment

### Production Setup
1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Environment Variables**
   Set `FLASK_ENV=production` for production mode

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY website_requirements.txt .
RUN pip install -r website_requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── clan.html         # Clan search page
│   ├── player.html       # Player search page
│   └── commands.html     # Commands documentation
├── static/               # Static assets
│   ├── css/
│   │   └── style.css    # Custom styles
│   ├── js/
│   │   └── main.js      # JavaScript functionality
│   └── images/          # Image assets
├── commands/             # Original Discord bot commands
├── website_requirements.txt # Web app dependencies
└── README.md            # This file
```

## 🔧 Development

### Local Development
1. Set `FLASK_ENV=development` in your `.env` file
2. Enable debug mode: `FLASK_DEBUG=True`
3. The application will auto-reload on file changes

### Adding Features
1. Create new routes in `app.py`
2. Add corresponding templates in `templates/`
3. Update navigation in `base.html`
4. Add custom styling in `style.css`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Troubleshooting
- **API Token Issues**: Ensure your COC API token is valid and for the correct IP
- **Missing Data**: Some features require the clan to be in war or CWL
- **Performance**: Large clans may take longer to load due to member data

### Getting Help
- Check the console for error messages
- Verify your API token and network connection
- Ensure all dependencies are installed correctly

## 🔄 Updates

The website automatically fetches the latest data from the Clash of Clans API. No manual updates required for game data.

## 🎯 Future Enhancements

- [ ] Player comparison tools
- [ ] Clan war history
- [ ] Advanced statistics and analytics
- [ ] Export functionality for data
- [ ] Multi-language support
- [ ] Bookmark favorite clans/players

---

**Built with ❤️ for the Clash of Clans community**