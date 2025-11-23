$headers = @{
    "Content-Type" = "application/json"
}

# 1. Create Medication
$body = '{"name": "Aspirin", "dosage_mg": 100, "prescribed_per_day": 2}'
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/medications/" -Method Post -Headers $headers -Body $body
Write-Host "Created Medication:"
$response | ConvertTo-Json

# 2. Get Medications
$medications = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/medications/" -Method Get
Write-Host "Medications List:"
$medications | ConvertTo-Json

$medId = $medications[0].id

# 2.5 Update and Delete Medication (Test)
# Update
$updateBody = '{"name": "Aspirin Updated", "dosage_mg": 150, "prescribed_per_day": 3}'
$updateResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/medications/$medId/" -Method Put -Headers $headers -Body $updateBody
Write-Host "Updated Medication:"
$updateResponse | ConvertTo-Json

# Verify Update
$updatedMed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/medications/$medId/" -Method Get
Write-Host "Verified Updated Medication:"
$updatedMed | ConvertTo-Json

# 3. Create Log
$bodyLog = '{"medication": ' + $medId + ', "taken_at": "2023-10-27T10:00:00Z", "was_taken": true}'
$responseLog = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/logs/" -Method Post -Headers $headers -Body $bodyLog
Write-Host "Created Log:"
$responseLog | ConvertTo-Json

# 4. Get Logs
$logs = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/logs/" -Method Get
Write-Host "Logs List:"
$logs | ConvertTo-Json

# 5. Filter Logs
$filterUrl = "http://127.0.0.1:8000/api/logs/filter/?start=2023-10-01&end=2023-10-30"
$filteredLogs = Invoke-RestMethod -Uri $filterUrl -Method Get
Write-Host "Filtered Logs:"
$filteredLogs | ConvertTo-Json

# 6. Get Medication Info
$infoUrl = "http://127.0.0.1:8000/api/medications/" + $medId + "/info/"
try {
    $info = Invoke-RestMethod -Uri $infoUrl -Method Get
    Write-Host "Medication Info:"
    $info | ConvertTo-Json
} catch {
    Write-Host "Medication Info failed (expected if no external API key or network issue): $_"
}

# 7. Delete Medication
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/medications/$medId/" -Method Delete
Write-Host "Deleted Medication $medId"
