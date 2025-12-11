$ErrorActionPreference = "Stop"

try {
    # Load Windows Runtime types
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject
    
    # This magic line helps load WinRT types in PS 5.1/7
    $null = [Windows.Devices.Sensors.Accelerometer, Windows.Devices.Sensors, ContentType=WindowsRuntime]
    
    $accel = [Windows.Devices.Sensors.Accelerometer]::GetDefault()
    
    if ($null -ne $accel) {
        Write-Host "Accelerometer: FOUND"
        $reading = $accel.GetCurrentReading()
        if ($null -ne $reading) {
             Write-Host "X: $($reading.AccelerationX)"
             Write-Host "Y: $($reading.AccelerationY)"
             Write-Host "Z: $($reading.AccelerationZ)"
        } else {
             Write-Host "Reading is null"
        }
    } else {
        Write-Host "Accelerometer: NOT FOUND (GetDefault returned null)"
    }
} catch {
    Write-Host "Error: $_"
    Write-Host "Ensure you are running on Windows 10/11 and hardware is present."
}
