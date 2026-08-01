# Script to update Attractions page with better font visibility
(Get-Content "pages\2_🎭_Attractions.py") -replace 'text_shadow = "2px 2px 8px rgba\(0, 0, 0, 0\.8\)"', 'text_shadow = "0 0 20px rgba(0,0,0,0.9), 2px 2px 12px rgba(0,0,0,0.95), 0 0 8px rgba(0,0,0,0.85)"' -replace 'text_shadow = "1px 1px 3px rgba\(255, 255, 255, 0\.9\)"', 'text_shadow = "0 0 15px rgba(255,255,255,0.95), 1px 1px 8px rgba(255,255,255,1), 0 0 6px rgba(255,255,255,0.9)"' | Set-Content "pages\2_🎭_Attractions.py"

Write-Host "✅ Updated Attractions page with better text visibility!" -ForegroundColor Green
