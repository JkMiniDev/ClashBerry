# ClashBerry - Clash of Clans Stats Portal
## Frontend-Only Website

A modern, responsive web application that provides comprehensive Clash of Clans statistics and analysis. Search for clan and player data with detailed analytics. Built with pure HTML, CSS, and JavaScript - **no backend required**.

## 🌟 Features

### 🚀 Frontend-Only Architecture
- **No Server Required**: Pure HTML, CSS & JavaScript
- **Custom API Integration**: Uses your proxy API endpoint
- **Modern UI**: Responsive Bootstrap 5 design with custom styling
- **Real-time Data**: Direct integration with your Clash of Clans proxy API

### 🔍 Search Features
- **Clan Search**: Comprehensive clan information, member lists, and war data
- **Player Search**: Detailed player statistics, achievements, and troop information
- **War Data**: Current war status and CWL group information
- **URL Parameters**: Direct linking to specific clans/players

### 🎨 User Experience
- **Responsive Design**: Works on all devices and screen sizes
- **Interactive Elements**: Sortable tables, progress animations, tooltips
- **Search History**: Local storage for recent searches
- **Keyboard Shortcuts**: Ctrl+K for quick search access
- **Error Handling**: Comprehensive error messages and fallbacks

## 🚀 Quick Start

### Prerequisites
- Web browser with JavaScript enabled
- Web server (for local development) or hosting platform

### Installation

1. **Download the files**
   ```bash
   # All files are already created in your workspace
   ```

2. **Open in a web server**
   ```bash
   # Option 1: Python simple server
   python3 -m http.server 8000
   
   # Option 2: Node.js serve
   npx serve .
   
   # Option 3: PHP built-in server
   php -S localhost:8000
   ```

3. **Access the website**
   Open `http://localhost:8000` in your browser

### Configuration

The API configuration is already set up in `js/api.js`:
```javascript
const API_CONFIG = {
    baseURL: 'https://api.jktripuri.site',
    token: 'JkMiniDev%1998'
};
```

**Important:** The API calls now correctly format tags by replacing `#` with `%23` and use `Bearer` authentication, matching your working implementation.

## 📁 Project Structure

```
├── index.html              # Homepage with features overview
├── clan.html               # Clan search and display page
├── player.html             # Player search and display page
├── commands.html           # ClashBerry features showcase
├── css/
│   └── style.css          # Custom styles and animations
└── js/
    ├── api.js             # API integration with your proxy
    ├── main.js            # General utilities and interactions
    ├── clan.js            # Clan search functionality
    ├── player.js          # Player search functionality
    └── commands.js        # Commands page functionality
```

## 🔧 API Integration

### Your Custom Proxy API
- **Base URL**: `https://api.jktripuri.site`
- **Token**: `JkMiniDev%1998`
- **Endpoints Used**:
  - `/clans/{clanTag}` - Clan information
  - `/players/{playerTag}` - Player information
  - `/clans/{clanTag}/currentwar` - Current war data
  - `/clans/{clanTag}/currentwar/leaguegroup` - CWL data

### Error Handling
The website includes comprehensive error handling for:
- Invalid clan/player tags
- API timeouts
- Network errors
- Missing data

## 📱 Features Overview

### Homepage (`index.html`)
- Hero section with call-to-action buttons
- Feature cards for each main function
- Quick start examples with real clan/player tags
- Modern, responsive design

### Clan Search (`clan.html`)
- Search form with tag validation
- Comprehensive clan information display
- Member list with sortable columns
- Current war status and statistics
- CWL group information when available
- Clickable player tags for easy navigation

### Player Search (`player.html`)
- Player search with tag validation
- Detailed player statistics and progression
- Achievement tracking with progress bars
- Troop, spell, and hero levels display
- League information and trophy counts
- Clan membership with quick clan access

### Commands Showcase (`commands.html`)
- Interactive showcase of ClashBerry features and capabilities
- Usage examples and feature descriptions
- Web alternatives for applicable commands
- Command categorization with icons

## ⚡ Interactive Features

### Search Functionality
- **Tag Validation**: Automatic format validation
- **Auto-formatting**: Removes # symbols automatically
- **Search History**: Stores recent searches in localStorage
- **URL Parameters**: Direct linking support

### Data Display
- **Sortable Tables**: Click column headers to sort
- **Progress Animations**: Animated progress bars
- **Responsive Design**: Adapts to all screen sizes
- **Loading States**: Shows progress while fetching data

### User Experience
- **Toast Notifications**: Success/error messages
- **Keyboard Shortcuts**: Ctrl+K for search, Escape to clear
- **Copy to Clipboard**: Click to copy tags
- **Search History**: Autocomplete from previous searches

## 🎨 Customization

### Styling
- Modify `css/style.css` for visual changes
- Bootstrap 5 classes for rapid styling
- CSS custom properties for easy theme changes
- Responsive breakpoints for all devices

### API Configuration
Update the API settings in `js/api.js`:
```javascript
const API_CONFIG = {
    baseURL: 'your-api-endpoint',
    token: 'your-api-token'
};
```

### Adding Features
1. Create new HTML templates
2. Add corresponding JavaScript functionality
3. Update navigation in all HTML files
4. Add custom styling as needed

## 🚀 Deployment

### Static Hosting
The website can be deployed to any static hosting platform:

- **Netlify**: Drag and drop the folder
- **Vercel**: Import from GitHub
- **GitHub Pages**: Push to gh-pages branch
- **Firebase Hosting**: Use Firebase CLI
- **AWS S3**: Upload as static website

### Local Development
```bash
# Python
python3 -m http.server 8000

# Node.js
npx serve .

# PHP
php -S localhost:8000
```

## 🛠️ Browser Support

- **Modern Browsers**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Features Used**: Fetch API, ES6+, CSS Grid, Flexbox
- **Responsive Design**: All screen sizes supported
- **Accessibility**: ARIA labels and semantic HTML

## 🔧 Development

### File Overview
- **HTML Files**: Semantic structure with Bootstrap components
- **CSS**: Custom styling with animations and responsive design
- **JavaScript**: Modular ES6 code with error handling

### Best Practices
- Semantic HTML structure
- Progressive enhancement
- Error handling and fallbacks
- Mobile-first responsive design
- Performance optimization

## 📊 Performance

- **Lightweight**: No heavy frameworks or dependencies
- **Fast Loading**: Optimized assets and minimal requests
- **Caching**: Browser caching for static assets
- **CDN**: Bootstrap and FontAwesome from CDN

## 🆘 Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure your API supports CORS
2. **API Rate Limits**: Handle 429 responses gracefully
3. **Invalid Tags**: User-friendly error messages
4. **Network Issues**: Offline detection and retry logic

### Debug Mode
Open browser console to see:
- API request/response logs
- Performance metrics
- Error details

## 🔄 Updates

To update the website:
1. Modify the relevant HTML, CSS, or JavaScript files
2. Test locally using a web server
3. Deploy to your hosting platform

## 🤝 Contributing

1. Fork or download the project
2. Make your changes
3. Test thoroughly
4. Submit improvements

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for the Clash of Clans community**

### Quick Commands
```bash
# Start local server
python3 -m http.server 8000

# Access website
open http://localhost:8000

# Test clan search
http://localhost:8000/clan.html?tag=2Y9L0RYR0

# Test player search
http://localhost:8000/player.html?tag=2PP
```