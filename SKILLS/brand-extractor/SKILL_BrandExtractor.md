---
name: brand-extractor
description: Extracts brand identity (colors, typography, spacing, etc.) from a website and updates the Brand Guidelines skill. Use this when you want to adapt the agent's output style to match a specific website or company brand.
license: MIT
---

# Brand Extractor

## Overview

This skill allows you to "steal" or replicate the brand identity of any website. It uses Firecrawl to scrape branding elements and then updates the `brand-guidelines` skill to enforce this new brand.

## Workflow

1.  **Get Target URL**: Ask the user for the website URL they want to extract branding from (if not provided).
2.  **Scrape Branding**:
    *   Execute the bundled python script:
        ```bash
        python3 brand-extractor/scripts/scrape_branding.py <URL>
        ```
    *   Ensure the `FIRECRAWL_API_KEY` is set in the environment (or .env file).
    *   This script outputs the JSON response from Firecrawl containing both `branding` and `extract` data, and automatically downloads images to `brand_assets/<domain>/`.
3.  **Analyze Output**:
    *   Read the stdout from the script execution.
    *   **Branding Object**: Contains fields like `colors` (primary, secondary, background, text), `typography` (headings, body).
    *   **Extract Object**: Contains `logo_url`, `hero_image_url`, `button_styles`, and `design_notes`.
    *   **Local Assets**: The output will also contain `local_assets` mapping (e.g., `logo` -> `Path/to/logo.png`).
4.  **Update Brand Guidelines**:
    *   Read the file `brand-guidelines/SKILL_BrandGuidelines.md`.
    *   Update the following sections based on the scraped data:
        *   **Title/Overview**: Change "Anthropic Brand Styling" to "[Company Name] Brand Styling".
        *   **Colors**: Replace the hex codes and descriptions using the `branding` colors.
        *   **Typography**: Update the font names for Headings and Body.
        *   **Images/Assets**: Note the location of downloaded assets (`brand_assets/`) and consider adding them to an `Assets` section in the guidelines if appropriate.
        *   **UI Elements/Buttons**: Use the `extract.button_styles` data to update any button definitions (border-radius, shadows, hover states if noted).
        *   **Design Vibe**: Use `design_notes` to update the general style description.
    *   **Self-Correction**: If the scrape misses some data (e.g., no font found), explicitly state "Default/System" or keep a sensible fallback, but try to be as accurate to the source as possible.

## Example Usage

User: "Extract the brand from stripe.com"

Agent:
1. Runs `python3 brand-extractor/scripts/scrape_branding.py https://stripe.com`
2. Receives JSON output.
3. Edits `brand-guidelines/SKILL_BrandGuidelines.md` to updated colors and fonts.
