# Smoke test — requires n8n running with workflow active
param(
    [string]$BaseUrl = "http://localhost:5678",
    [string]$Secret = $env:WEBHOOK_SECRET
)

$uri = "$BaseUrl/webhook/linkedin-ai-post"
$headers = @{ "Content-Type" = "application/json" }
if ($Secret) { $headers["X-Webhook-Secret"] = $Secret }

$body = @{
    topic = "Smoke test — please ignore"
    dry_run = $true
} | ConvertTo-Json

Write-Host "POST $uri"
$response = Invoke-RestMethod -Method POST -Uri $uri -Headers $headers -Body $body

if (-not $response.success) {
    Write-Error "Smoke test failed: $($response | ConvertTo-Json -Depth 5)"
    exit 1
}

Write-Host "Smoke test passed (dry_run preview)."
$response | ConvertTo-Json -Depth 5