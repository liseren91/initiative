# Configure Railway project "resourceful-alignment" for Initiative backend.
# Reads secrets from backend/.env and Railway API key from ~/.cursor/mcp.json.
# Does not print secret values.

$ErrorActionPreference = "Stop"

$ProjectId = "94d635ad-ef9d-472e-9a00-e8e8d8e45315"
$EnvironmentId = "c75ce26a-a703-46a0-8286-4c2be6903f96"
$ServiceId = "10fc3b35-7878-4080-974e-0a1c7caab190"
$PublicDomain = "https://initiative-dev-production.up.railway.app"
$GraphQlUrl = "https://backboard.railway.app/graphql/v2"

function Get-RailwayToken {
    $mcpPath = Join-Path $env:USERPROFILE ".cursor\mcp.json"
    if (-not (Test-Path $mcpPath)) {
        throw "Railway API key not found in $mcpPath"
    }
    $config = Get-Content $mcpPath | ConvertFrom-Json
    return $config.mcpServers.railway.env.RAILWAY_API_KEY
}

function Read-DotEnv([string]$Path) {
    $values = @{}
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 1) { return }
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim()
        $values[$key] = $val
    }
    return $values
}

function Invoke-RailwayGraphQl {
    param(
        [string]$Token,
        [string]$Query,
        [hashtable]$Variables = @{}
    )

    $payload = @{ query = $Query }
    if ($Variables.Count -gt 0) {
        $payload.variables = $Variables
    }

    $json = $payload | ConvertTo-Json -Depth 20 -Compress
    $tmp = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tmp, $json, [System.Text.UTF8Encoding]::new($false))

    try {
        $response = curl.exe -s -X POST $GraphQlUrl `
            -H "Authorization: Bearer $Token" `
            -H "Content-Type: application/json" `
            --data-binary "@$tmp"
        $parsed = $response | ConvertFrom-Json
        if ($parsed.errors) {
            throw ($parsed.errors | ConvertTo-Json -Compress)
        }
        return $parsed.data
    }
    finally {
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $repoRoot "backend\.env"
if (-not (Test-Path $envPath)) {
    throw "Missing backend/.env. Copy env.template and fill required values first."
}

$localEnv = Read-DotEnv $envPath
$required = @("SECRET_KEY", "DATABASE_URL", "DATABASE_URL_APP", "DATABASE_URL_ADMIN")
foreach ($name in $required) {
    if (-not $localEnv.ContainsKey($name) -or -not $localEnv[$name]) {
        throw "backend/.env is missing required variable: $name"
    }
}

$token = Get-RailwayToken

Write-Host "Updating service instance settings..."
Invoke-RailwayGraphQl -Token $token -Query @'
mutation ServiceInstanceUpdate($serviceId: String!, $environmentId: String!, $input: ServiceInstanceUpdateInput!) {
  serviceInstanceUpdate(serviceId: $serviceId, environmentId: $environmentId, input: $input)
}
'@ -Variables @{
    serviceId = $ServiceId
    environmentId = $EnvironmentId
    input = @{
        rootDirectory = "backend"
        buildCommand = "pip install -r requirements.txt"
        startCommand = 'uvicorn app.main:app --host 0.0.0.0 --port $PORT'
    }
} | Out-Null

Write-Host "Setting backend environment variables..."
$railwayVars = @{
    SECRET_KEY = $localEnv.SECRET_KEY
    DATABASE_URL = $localEnv.DATABASE_URL
    DATABASE_URL_APP = $localEnv.DATABASE_URL_APP
    DATABASE_URL_ADMIN = $localEnv.DATABASE_URL_ADMIN
    APP_URL = $PublicDomain
    BEHIND_PROXY = "true"
    ENABLE_PUBLIC_REGISTRATION = if ($localEnv.ENABLE_PUBLIC_REGISTRATION) { $localEnv.ENABLE_PUBLIC_REGISTRATION } else { "true" }
    DISABLE_GUILD_CREATION = if ($localEnv.DISABLE_GUILD_CREATION) { $localEnv.DISABLE_GUILD_CREATION } else { "false" }
    ACCESS_TOKEN_EXPIRE_MINUTES = if ($localEnv.ACCESS_TOKEN_EXPIRE_MINUTES) { $localEnv.ACCESS_TOKEN_EXPIRE_MINUTES } else { "1440" }
}

if ($localEnv.FIRST_SUPERUSER_EMAIL) { $railwayVars.FIRST_SUPERUSER_EMAIL = $localEnv.FIRST_SUPERUSER_EMAIL }
if ($localEnv.FIRST_SUPERUSER_PASSWORD) { $railwayVars.FIRST_SUPERUSER_PASSWORD = $localEnv.FIRST_SUPERUSER_PASSWORD }
if ($localEnv.FIRST_SUPERUSER_FULL_NAME) { $railwayVars.FIRST_SUPERUSER_FULL_NAME = $localEnv.FIRST_SUPERUSER_FULL_NAME }

Invoke-RailwayGraphQl -Token $token -Query @'
mutation VariableCollectionUpsert($input: VariableCollectionUpsertInput!) {
  variableCollectionUpsert(input: $input)
}
'@ -Variables @{
    input = @{
        projectId = $ProjectId
        environmentId = $EnvironmentId
        serviceId = $ServiceId
        variables = $railwayVars
        replace = $false
        skipDeploys = $true
    }
} | Out-Null

Write-Host "Triggering redeploy..."
Invoke-RailwayGraphQl -Token $token -Query @'
mutation Redeploy($serviceId: String!, $environmentId: String!) {
  serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
}
'@ -Variables @{
    serviceId = $ServiceId
    environmentId = $EnvironmentId
} | Out-Null

Write-Host "Done."
Write-Host "Project: resourceful-alignment"
Write-Host "Service: initiative-dev"
Write-Host "URL: $PublicDomain"
Write-Host "Health: $PublicDomain/api/v1/version"
