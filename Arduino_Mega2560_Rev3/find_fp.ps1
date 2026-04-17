$files = @(
    'D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Rev3\Arduino Mega 2560.kicad_sch',
    'D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Rev3\ATMEGA2560-16AU.kicad_sch',
    'D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Rev3\Power.kicad_sch',
    'D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Rev3\Headers.kicad_sch'
)

foreach ($file in $files) {
    Write-Host "`n=== $([System.IO.Path]::GetFileName($file)) ==="
    $lines = Get-Content $file
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match 'property "Footprint" ""') {
            $ref = '?'; $val = '?'
            for ($j = $i; $j -gt [Math]::Max(0,$i-20); $j--) {
                if ($lines[$j] -match 'property "Reference" "([^"]+)"') { $ref = $Matches[1]; break }
            }
            for ($j = $i; $j -gt [Math]::Max(0,$i-20); $j--) {
                if ($lines[$j] -match 'property "Value" "([^"]+)"') { $val = $Matches[1]; break }
            }
            if ($ref -notmatch '^#' -and $ref -ne '?') {
                Write-Host ('{0,-12} {1,-25} line {2}' -f $ref, $val, ($i+1))
            }
        }
    }
}
