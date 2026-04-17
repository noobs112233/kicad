Set-Location 'D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Rev3'

$fileLibEnd = @{
    'Arduino Mega 2560.kicad_sch'  = 3823
    'ATMEGA2560-16AU.kicad_sch'    = 3236
    'Power.kicad_sch'              = 2820
    'Headers.kicad_sch'            = 3178
}

foreach ($f in $fileLibEnd.Keys) {
    Write-Host "`n=== $f ==="
    $lines = Get-Content $f
    $libEnd = $fileLibEnd[$f]

    for ($i = $libEnd; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match 'property "Footprint" "([^"]*)"') {
            $fp = $Matches[1]
            $ref = '?'; $val = '?'
            for ($j = $i; $j -gt [Math]::Max($libEnd,$i-30); $j--) {
                if ($lines[$j] -match 'property "Reference" "([^"]+)"') { $ref = $Matches[1] }
                if ($lines[$j] -match 'property "Value" "([^"]+)"') { $val = $Matches[1] }
            }
            if ($ref -notmatch '^#') {
                $mark = if ($fp -eq '') { ' <<< MISSING' } else { '' }
                Write-Host ('{0,-12} {1,-22} {2}{3}' -f $ref, $val, $fp, $mark)
            }
        }
    }
}
