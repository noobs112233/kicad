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

    # Only look at placed instances (after lib_symbols)
    for ($i = $libEnd; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match 'property "Footprint" ""') {
            $ref = '?'; $val = '?'; $libid = '?'
            for ($j = $i; $j -gt [Math]::Max($libEnd,$i-30); $j--) {
                if ($lines[$j] -match 'property "Reference" "([^"]+)"') { $ref = $Matches[1] }
                if ($lines[$j] -match 'property "Value" "([^"]+)"') { $val = $Matches[1] }
                if ($lines[$j] -match 'lib_id "([^"]+)"') { $libid = $Matches[1] }
            }
            if ($ref -notmatch '^#') {
                Write-Host ('{0,-12} {1,-25} [{2}] line {3}' -f $ref, $val, $libid, ($i+1))
            }
        }
    }
}
