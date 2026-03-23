# 🚀 GitHub Profile Portfolio Generator

Turn your GitHub profile into a stunning, professional developer portfolio website in seconds. No coding required.

![Portfolio Preview](file:///C:/Users/HP/.gemini/antigravity/brain/95cc5b78-c60a-4a9c-99a4-54846bdbd732/.system_generated/click_feedback/click_feedback_1774281969970.png)

## ✨ Features

- **Automated Data Fetching**: Pulls your profile info, top repositories, language stats, and contributions directly from the GitHub API.
- **Premium Themes**: Choose from 4 professionally designed, high-impact themes:
  - 🌌 **Midnight Dark**: Deep space aesthetic with purple accents.
  - 🌊 **Ocean Blue**: Clean, professional blue with teal highlights.
  - 🌅 **Sunset Glow**: Vibrant, warm colors with a modern feel.
  - 🌲 **Forest Green**: Grounded, tech-organic look with emerald tones.
- **Modern Hero Redesign**: Dynamic layouts featuring large, morphing avatars and glowing effects.
- **Interactive Charts**: Responsive skill visualizations powered by Chart.js.
- **Download & Deploy**: One-click ZIP download of your generated static site, ready for GitHub Pages, Vercel, or Netlify.
- **API Robustness**: Built-in retry logic and session management for stable connections.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- [GitHub Personal Access Token](https://github.com/settings/tokens) (Recommended to avoid rate limits)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sakshere/Github-Profile-Portfolio-Generator.git
   cd Github-Profile-Portfolio-Generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Rename `.env.example` to `.env` and add your GitHub token:
   ```env
   GITHUB_TOKEN=your_personal_access_token_here
   FLASK_SECRET_KEY=any_random_string
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```
   Open `http://localhost:5000` in your browser.

## 💡 Usage Tips

- **Avoid Rate Limits**: GitHub restricts unauthenticated requests to 60/hr. Using a `GITHUB_TOKEN` increases this to 5,000/hr.
- **Customization**: You can further customize the generated code by editing the `templates/portfolio/` directory.

## 📄 License
Built as a Capstone Project. Use it to showcase your best work to the world!