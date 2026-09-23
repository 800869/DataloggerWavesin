param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Config,
    [string]$TaskName = 'DataloggerWavesin'
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$pythonPath = (Resolve-Path -LiteralPath $Python).Path
$configPath = (Resolve-Path -LiteralPath $Config).Path
$entryPath = Join-Path $projectRoot 'scripts\adquisicion.py'
& $pythonPath $entryPath --config $configPath --check
if ($LASTEXITCODE -ne 0) { throw 'Configuracion invalida' }
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    throw 'La tarea ya existe. Revisela antes de reemplazarla.'
}
$credential = Get-Credential -Message 'Cuenta Windows dedicada con Python, SSH, claves y known_hosts preparados'
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument ('"{0}" --config "{1}"' -f $entryPath,$configPath) -WorkingDirectory $projectRoot
$boot = New-ScheduledTaskTrigger -AtStartup
$watch = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($boot,$watch) -Settings $settings -User $credential.UserName -Password $credential.GetNetworkCredential().Password -Description 'Adquisicion Wavenis en PC y servidor Modbus TCP'
Write-Host 'Tarea registrada. El disparador periodico la iniciara en aproximadamente un minuto.'
