"""Styling system module with design tokens and CSS generation.

This module provides centralized design tokens (colors, typography, spacing)
and generates the complete CSS stylesheet for the application with glass-morphism
effects and premium typography.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.7
"""

from typing import Final


class DesignTokens:
    """Design system tokens for consistent styling across the application.
    
    This class defines the core design elements including color palette,
    typography, spacing, and visual effects.
    """
    
    # Color palette
    INK: Final[str] = "#111827"
    MUTED: Final[str] = "#4b5563"
    ACCENT: Final[str] = "#df5d43"
    GOLD: Final[str] = "#bf821d"
    SURFACE: Final[str] = "rgba(255, 255, 255, .91)"
    
    # Typography
    FONT_BODY: Final[str] = "'DM Sans', Arial, sans-serif"
    FONT_DISPLAY: Final[str] = "'Playfair Display', Georgia, serif"
    
    # Spacing
    BORDER_RADIUS: Final[str] = "20px"
    CARD_PADDING: Final[str] = "1.8rem"
    
    # Effects
    GLASS_BACKDROP_BLUR: Final[str] = "blur(14px)"
    CARD_SHADOW: Final[str] = "0 16px 42px rgba(23, 45, 68, .18)"
    HOVER_TRANSFORM: Final[str] = "translateY(-2px)"


def get_base_styles() -> str:
    """Generate the complete CSS stylesheet for the application.
    
    Returns glass-morphism cards, premium typography, smooth transitions,
    and responsive layout styles.
    
    Returns:
        Complete CSS stylesheet as an HTML style tag string
    """
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
    
    :root {
        --ink: #111827;
        --muted: #4b5563;
        --accent: #df5d43;
        --gold: #bf821d;
        --surface: rgba(255, 255, 255, .91);
    }
    
    /* Background gradient with parallax effect */
    .stApp {
        background: linear-gradient(115deg, rgba(255, 250, 243, .80), rgba(225, 245, 247, .72)),
            url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80") center/cover fixed;
    }
    
    /* Typography system */
    .stApp, .stApp p, .stApp label, .stApp span {
        font-family: 'DM Sans', Arial, sans-serif;
        color: var(--ink);
    }
    
    .stApp h1, .stApp h2, .stApp h3 {
        font-family: 'Playfair Display', Georgia, serif;
        font-weight: 700;
        color: #101b2d;
        letter-spacing: -.025em;
    }
    
    /* Glass-morphism cards */
    .card, [data-testid="stAlert"], [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 253, 249, .97);
        border: 1px solid rgba(255, 255, 255, .9);
        border-radius: 20px;
        box-shadow: 0 16px 42px rgba(23, 45, 68, .18);
        backdrop-filter: blur(14px);
        padding: 1.8rem;
    }
    
    /* Interactive button styles with elevation */
    .stButton > button {
        background: linear-gradient(135deg, #e4684d, #b7463a);
        border: 0;
        border-radius: 12px;
        color: #251510;
        font-weight: 700;
        box-shadow: 0 8px 18px rgba(178, 70, 58, .28);
        transition: transform .18s ease, box-shadow .18s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(178, 70, 58, .36);
    }
    </style>
    """
