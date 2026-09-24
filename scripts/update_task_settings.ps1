$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$tasks = @("NewsBriefing_08h", "NewsBriefing_13h", "NewsBriefing_19h")
foreach ($t in $tasks) {
    try {
        Set-ScheduledTask -TaskName $t -Settings $settings | Out-Null
        Write-Host "Sucesso ao atualizar: $t"
    } catch {
        Write-Host "Erro em $t : $_"
    }
}
