param(
    $action = "rebootDevice",
    $device = "ES740",
    $currentLocation = $PSScriptRoot,
    $commandFile = $currentLocation+"\Action\"+$action+".txt",
    $userName = 'root',
    $deviceName = '203.0.113.1',
    $ES740Key = 'developerKeyES740.ppk',
    $cTPGKey = 'putty_edp.ppk',
    $keyFile = $currentLocation+'\Data\',
    $puttyExe = $currentLocation+'\Data\putty.exe'
)

if ($device -match "ES740")
{
$deviceName = '203.0.113.1'
$keyFile = $keyFile+$ES740Key
}
if ($device -match "CTPG")
{
$deviceName = '192.168.1.40'
$keyFile = $keyFile+$cTPGKey
}

echo y | &($puttyExe) $userName@$deviceName -i $keyFile -m $commandFile
